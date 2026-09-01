"""
Tests for Phase 8: Risk Threshold Optimization & Decision Policy Engine.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.risk.thresholds import (
    MERCHANT_STRATEGY_PRESETS,
    MerchantCostParams,
    RiskTier,
    RiskTierConfig,
    compute_metrics_at_threshold,
    sweep_thresholds,
)

THRESHOLD_JSON_PATH = PROJECT_ROOT / "reports" / "threshold_optimization.json"
THRESHOLD_REPORT_PATH = PROJECT_ROOT / "reports" / "threshold-optimization-report.md"
THRESHOLD_CURVES_PATH = PROJECT_ROOT / "reports" / "figures" / "13_threshold_curves.png"


class TestRiskTierConfig:
    """Test suite for multi-tier risk level assignments."""

    def test_risk_tier_assignments_default(self):
        cfg = RiskTierConfig(low_cutoff=0.20, medium_cutoff=0.45, high_cutoff=0.70)
        assert cfg.assign_tier(0.05) == RiskTier.LOW
        assert cfg.assign_tier(0.199) == RiskTier.LOW
        assert cfg.assign_tier(0.20) == RiskTier.MEDIUM
        assert cfg.assign_tier(0.449) == RiskTier.MEDIUM
        assert cfg.assign_tier(0.45) == RiskTier.HIGH
        assert cfg.assign_tier(0.699) == RiskTier.HIGH
        assert cfg.assign_tier(0.70) == RiskTier.CRITICAL
        assert cfg.assign_tier(0.95) == RiskTier.CRITICAL

    def test_custom_tier_cutoffs(self):
        cfg = RiskTierConfig(low_cutoff=0.10, medium_cutoff=0.30, high_cutoff=0.60)
        assert cfg.assign_tier(0.08) == RiskTier.LOW
        assert cfg.assign_tier(0.25) == RiskTier.MEDIUM
        assert cfg.assign_tier(0.55) == RiskTier.HIGH
        assert cfg.assign_tier(0.85) == RiskTier.CRITICAL


class TestMerchantCostModel:
    """Test suite for financial cost and savings modeling."""

    def test_cost_params_ratio(self):
        params = MerchantCostParams(cost_fn_return=600.0, cost_fp_friction=150.0)
        assert params.cost_ratio == 4.0

    def test_compute_metrics_at_threshold(self):
        y_true = np.array([0, 0, 1, 1, 0, 1])
        y_prob = np.array([0.1, 0.2, 0.4, 0.8, 0.3, 0.9])
        params = MerchantCostParams(cost_fn_return=600.0, cost_fp_friction=150.0)

        # Threshold 0.5: Preds = [0, 0, 0, 1, 0, 1]
        # TP=2, FP=0, TN=3, FN=1
        metrics = compute_metrics_at_threshold(
            y_true, y_prob, threshold=0.5, cost_params=params,
            do_nothing_total_cost=1800.0, naive_50_total_cost=600.0
        )

        assert metrics.true_positives == 2
        assert metrics.false_positives == 0
        assert metrics.false_negatives == 1
        assert metrics.true_negatives == 3
        assert metrics.total_cost_inr == 600.0
        assert metrics.net_savings_vs_do_nothing_inr == 1200.0

    def test_sweep_thresholds_optimality(self):
        y_true = np.array([0] * 70 + [1] * 30)
        y_prob = np.linspace(0.05, 0.95, 100)
        params = MerchantCostParams(cost_fn_return=600.0, cost_fp_friction=150.0)

        metrics_list, summary = sweep_thresholds(y_true, y_prob, params, num_thresholds=50)

        assert len(metrics_list) == 50
        assert "optimal_cost_threshold" in summary
        assert "optimal_f1_threshold" in summary

        opt_cost = summary["optimal_cost_threshold"]
        assert 0.01 <= opt_cost["threshold"] <= 0.99
        assert opt_cost["net_savings_vs_do_nothing_inr"] >= 0


class TestMerchantStrategyPresets:
    """Test suite for configurable merchant strategy profiles."""

    def test_presets_exist(self):
        assert "Conservative (Growth & Frictionless)" in MERCHANT_STRATEGY_PRESETS
        assert "Balanced (Default Cost-Optimal)" in MERCHANT_STRATEGY_PRESETS
        assert "Aggressive (Margin & Return Defense)" in MERCHANT_STRATEGY_PRESETS

    def test_preset_threshold_ordering(self):
        cons_cut = MERCHANT_STRATEGY_PRESETS["Conservative (Growth & Frictionless)"]["tier_config"].low_cutoff
        bal_cut = MERCHANT_STRATEGY_PRESETS["Balanced (Default Cost-Optimal)"]["tier_config"].low_cutoff
        agg_cut = MERCHANT_STRATEGY_PRESETS["Aggressive (Margin & Return Defense)"]["tier_config"].low_cutoff

        assert cons_cut > bal_cut > agg_cut


class TestThresholdOptimizationArtifacts:
    """Test suite verifying generated reports and JSON outputs."""

    def test_artifacts_exist(self):
        assert THRESHOLD_JSON_PATH.exists(), f"Missing JSON at {THRESHOLD_JSON_PATH}"
        assert THRESHOLD_REPORT_PATH.exists(), f"Missing report at {THRESHOLD_REPORT_PATH}"
        assert THRESHOLD_CURVES_PATH.exists(), f"Missing curves plot at {THRESHOLD_CURVES_PATH}"

    def test_json_contents_valid(self):
        with open(THRESHOLD_JSON_PATH) as f:
            data = json.load(f)

        assert "balanced_sweep_summary" in data
        assert "balanced_tier_breakdown" in data
        assert "preset_strategy_comparisons" in data

        opt_cost = data["balanced_sweep_summary"]["optimal_cost_threshold"]
        assert abs(opt_cost["threshold"] - 0.20) < 0.02
        assert opt_cost["net_savings_vs_do_nothing_inr"] > 1_000_000.0
        assert opt_cost["net_savings_vs_naive_50_inr"] > 500_000.0

    def test_report_sections_present(self):
        content = THRESHOLD_REPORT_PATH.read_text(encoding="utf-8")
        assert "Executive Summary & Cost-Optimal Threshold" in content
        assert "Visual Optimization Curves" in content
        assert "Actionable Multi-Tier Risk System" in content
        assert "Merchant Strategy Presets Comparison" in content
