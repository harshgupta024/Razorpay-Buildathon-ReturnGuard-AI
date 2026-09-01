"""
ReturnGuard AI — Risk Threshold Optimization & Tier Assignment Module

Defines:
1. Asymmetric business cost model for threshold evaluation
2. Threshold sweep & multi-objective optimization (Max F1 vs Min Business Cost)
3. Actionable multi-tier risk boundaries (LOW, MEDIUM, HIGH, CRITICAL)
4. Merchant risk strategy presets (Conservative, Balanced, Aggressive)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score


class RiskTier(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskTierConfig:
    """Configurable probability cutoffs defining risk levels."""
    low_cutoff: float = 0.20       # Below this: LOW risk (friction-less)
    medium_cutoff: float = 0.45    # [low, medium): MEDIUM risk (soft mitigation)
    high_cutoff: float = 0.70      # [medium, high): HIGH risk (firm mitigation)
                                   # >= high_cutoff: CRITICAL risk (manual review / strict)

    def assign_tier(self, probability: float) -> RiskTier:
        """Assign categorical risk tier based on calibrated return probability."""
        if probability < self.low_cutoff:
            return RiskTier.LOW
        elif probability < self.medium_cutoff:
            return RiskTier.MEDIUM
        elif probability < self.high_cutoff:
            return RiskTier.HIGH
        else:
            return RiskTier.CRITICAL


@dataclass
class MerchantCostParams:
    """Configurable merchant cost assumptions for FP and FN trade-offs (in INR ₹)."""
    cost_fn_return: float = 600.0  # Cost of a missed return (shipping + restocking + depreciation)
    cost_fp_friction: float = 150.0  # Cost of unnecessary friction on a safe customer order

    @property
    def cost_ratio(self) -> float:
        """Ratio of False Negative cost to False Positive cost."""
        return self.cost_fn_return / self.cost_fp_friction if self.cost_fp_friction > 0 else 1.0


@dataclass
class ThresholdMetrics:
    """Evaluation metrics at a specific decision threshold."""
    threshold: float
    precision: float
    recall: float
    f1: float
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    total_cost_inr: float
    cost_per_order_inr: float
    net_savings_vs_do_nothing_inr: float
    net_savings_vs_naive_50_inr: float


def compute_metrics_at_threshold(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float,
    cost_params: MerchantCostParams,
    do_nothing_total_cost: float,
    naive_50_total_cost: float,
) -> ThresholdMetrics:
    """Compute performance and business financial metrics at a single threshold."""
    y_pred = (y_prob >= threshold).astype(int)

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    total_cost = float((fp * cost_params.cost_fp_friction) + (fn * cost_params.cost_fn_return))
    cost_per_order = total_cost / len(y_true) if len(y_true) > 0 else 0.0

    savings_vs_do_nothing = do_nothing_total_cost - total_cost
    savings_vs_naive = naive_50_total_cost - total_cost

    return ThresholdMetrics(
        threshold=round(threshold, 3),
        precision=round(prec, 4),
        recall=round(rec, 4),
        f1=round(f1, 4),
        true_positives=int(tp),
        false_positives=int(fp),
        true_negatives=int(tn),
        false_negatives=int(fn),
        total_cost_inr=round(total_cost, 2),
        cost_per_order_inr=round(cost_per_order, 2),
        net_savings_vs_do_nothing_inr=round(savings_vs_do_nothing, 2),
        net_savings_vs_naive_50_inr=round(savings_vs_naive, 2),
    )


def sweep_thresholds(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    cost_params: MerchantCostParams | None = None,
    num_thresholds: int = 100,
) -> Tuple[List[ThresholdMetrics], Dict[str, Any]]:
    """
    Perform a complete threshold sweep across [0.01, 0.99] and identify optimal operating points.

    Returns:
        metrics_list: List of ThresholdMetrics across all evaluated thresholds
        summary: Summary dict identifying max F1 and min cost operating points
    """
    if cost_params is None:
        cost_params = MerchantCostParams()

    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob).astype(float)

    total_returns = int(np.sum(y_true))
    # Baseline 1: "Do Nothing" (predict 0 for all -> 0 FP, all returns are FN)
    do_nothing_total_cost = float(total_returns * cost_params.cost_fn_return)

    # Baseline 2: Naive 0.50 threshold
    naive_pred = (y_prob >= 0.50).astype(int)
    naive_cm = confusion_matrix(y_true, naive_pred, labels=[0, 1])
    _, naive_fp, naive_fn, _ = naive_cm.ravel()
    naive_50_total_cost = float((naive_fp * cost_params.cost_fp_friction) + (naive_fn * cost_params.cost_fn_return))

    thresholds = np.linspace(0.01, 0.99, num_thresholds)
    metrics_list: List[ThresholdMetrics] = []

    for t in thresholds:
        m = compute_metrics_at_threshold(
            y_true, y_prob, float(t), cost_params, do_nothing_total_cost, naive_50_total_cost
        )
        metrics_list.append(m)

    # Find optimal operating points
    max_f1_metric = max(metrics_list, key=lambda m: m.f1)
    min_cost_metric = min(metrics_list, key=lambda m: m.total_cost_inr)

    summary = {
        "total_orders_evaluated": len(y_true),
        "total_actual_returns": total_returns,
        "cost_params": {
            "cost_fn_missed_return_inr": cost_params.cost_fn_return,
            "cost_fp_friction_inr": cost_params.cost_fp_friction,
            "cost_ratio": cost_params.cost_ratio,
        },
        "baselines": {
            "do_nothing_cost_inr": round(do_nothing_total_cost, 2),
            "naive_50_cost_inr": round(naive_50_total_cost, 2),
        },
        "optimal_f1_threshold": {
            "threshold": max_f1_metric.threshold,
            "f1": max_f1_metric.f1,
            "precision": max_f1_metric.precision,
            "recall": max_f1_metric.recall,
            "total_cost_inr": max_f1_metric.total_cost_inr,
        },
        "optimal_cost_threshold": {
            "threshold": min_cost_metric.threshold,
            "total_cost_inr": min_cost_metric.total_cost_inr,
            "cost_per_order_inr": min_cost_metric.cost_per_order_inr,
            "net_savings_vs_do_nothing_inr": min_cost_metric.net_savings_vs_do_nothing_inr,
            "net_savings_vs_naive_50_inr": min_cost_metric.net_savings_vs_naive_50_inr,
            "precision": min_cost_metric.precision,
            "recall": min_cost_metric.recall,
            "f1": min_cost_metric.f1,
        },
    }

    return metrics_list, summary


# Strategy Presets for Merchants
MERCHANT_STRATEGY_PRESETS: Dict[str, Dict[str, Any]] = {
    "Conservative (Growth & Frictionless)": {
        "description": "Prioritizes minimal checkout friction. Only flags very high risk orders.",
        "cost_params": MerchantCostParams(cost_fn_return=600.0, cost_fp_friction=300.0),
        "tier_config": RiskTierConfig(low_cutoff=0.30, medium_cutoff=0.55, high_cutoff=0.75),
    },
    "Balanced (Default Cost-Optimal)": {
        "description": "Standard balanced trade-off minimizing total net return and friction costs.",
        "cost_params": MerchantCostParams(cost_fn_return=600.0, cost_fp_friction=150.0),
        "tier_config": RiskTierConfig(low_cutoff=0.20, medium_cutoff=0.45, high_cutoff=0.70),
    },
    "Aggressive (Margin & Return Defense)": {
        "description": "Strict defense against return abuse. Catches maximum returns even with added friction.",
        "cost_params": MerchantCostParams(cost_fn_return=800.0, cost_fp_friction=100.0),
        "tier_config": RiskTierConfig(low_cutoff=0.15, medium_cutoff=0.35, high_cutoff=0.60),
    },
}
