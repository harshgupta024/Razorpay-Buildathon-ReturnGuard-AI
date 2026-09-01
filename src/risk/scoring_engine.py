"""
ReturnGuard AI — Unified Production Risk Scoring Engine

The central inference engine orchestrating:
1. Feature Preprocessing (StandardScaler + OneHotEncoder)
2. Calibrated Machine Learning Model Inference
3. Risk Tier Categorization (LOW, MEDIUM, HIGH, CRITICAL)
4. Business Cost & Profit-Maximizing Mitigation Evaluation

Usage:
    from src.risk.scoring_engine import RiskScoringEngine

    engine = RiskScoringEngine()
    result = engine.score_order(order_dict)
"""

import logging
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import joblib
import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.business.cost_engine import (
    BusinessCostEngine,
    CostEngineAssessment,
    MitigationActionType,
    OrderFinancialProfile,
)
from src.ml.preprocessing import FeaturePreprocessor
from src.risk.thresholds import RiskTier, RiskTierConfig

logger = logging.getLogger(__name__)

MODELS_DIR = PROJECT_ROOT / "models"
DEFAULT_PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.joblib"
DEFAULT_CALIBRATED_MODEL_PATH = MODELS_DIR / "calibrated_model.joblib"


@dataclass
class OrderScoreResult:
    """Complete prediction, risk tier, and financial decision output for an order."""
    order_id: str
    customer_id: str
    product_id: str
    order_value: float
    product_category: str
    payment_method: str
    predicted_return_probability: float
    risk_score: float                   # Integer/float scale 0 - 100
    risk_tier: RiskTier
    risk_tier_name: str
    gross_return_loss_inr: float
    unmitigated_expected_loss_inr: float
    recommended_action: MitigationActionType
    recommended_action_name: str
    expected_net_savings_inr: float
    mitigated_expected_loss_inr: float
    action_rationale: str
    action_evaluations: List[Dict[str, Any]]
    scored_at: str
    latency_ms: float

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["risk_tier"] = self.risk_tier.value
        data["recommended_action"] = self.recommended_action.value
        return data


class RiskScoringEngine:
    """Production inference engine for real-time return risk scoring and decision support."""

    def __init__(
        self,
        preprocessor_path: Union[Path, str] = DEFAULT_PREPROCESSOR_PATH,
        model_path: Union[Path, str] = DEFAULT_CALIBRATED_MODEL_PATH,
        tier_config: Optional[RiskTierConfig] = None,
        cost_engine: Optional[BusinessCostEngine] = None,
    ):
        self.preprocessor_path = Path(preprocessor_path)
        self.model_path = Path(model_path)
        self.tier_config = tier_config or RiskTierConfig(low_cutoff=0.20, medium_cutoff=0.45, high_cutoff=0.70)
        self.cost_engine = cost_engine or BusinessCostEngine()

        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Load preprocessor and model artifacts from disk."""
        if not self.preprocessor_path.exists():
            raise FileNotFoundError(f"Preprocessor not found at {self.preprocessor_path}")
        if not self.model_path.exists():
            raise FileNotFoundError(f"Calibrated model not found at {self.model_path}")

        logger.info(f"Loading preprocessor from {self.preprocessor_path}...")
        self.preprocessor = FeaturePreprocessor.load(self.preprocessor_path)

        logger.info(f"Loading calibrated model from {self.model_path}...")
        self.model = joblib.load(self.model_path)
        logger.info("RiskScoringEngine ready for inference.")

    def score_order(self, order_data: Union[Dict[str, Any], pd.Series, pd.DataFrame]) -> OrderScoreResult:
        """Score a single order and compute optimal business mitigation."""
        start_time = time.perf_counter()

        # Format as 1-row DataFrame
        if isinstance(order_data, dict):
            df = pd.DataFrame([order_data])
        elif isinstance(order_data, pd.Series):
            df = pd.DataFrame([order_data.to_dict()])
        elif isinstance(order_data, pd.DataFrame):
            df = order_data.head(1).copy()
        else:
            raise TypeError(f"Unsupported order_data type: {type(order_data)}")

        # Extract identifiers & financial fields
        row = df.iloc[0]
        order_id = str(row.get("order_id", "ORD-UNKNOWN"))
        customer_id = str(row.get("customer_id", "CUST-UNKNOWN"))
        product_id = str(row.get("product_id", "PROD-UNKNOWN"))
        order_value = float(row.get("order_value", 2000.0))
        product_category = str(row.get("product_category", "Clothing"))
        payment_method = str(row.get("payment_method", "UPI"))
        weight_grams = float(row.get("product_weight_grams", 1000.0))

        # 1. Transform features & predict calibrated probability
        X = self.preprocessor.transform(df)
        X = np.ascontiguousarray(X, dtype=np.float32)
        prob = float(self.model.predict_proba(X)[0, 1])

        # 2. Risk Score & Tier Assignment
        risk_score = round(prob * 100.0, 1)
        risk_tier = self.tier_config.assign_tier(prob)

        # 3. Financial Loss & Mitigation Policy Simulation
        financial_profile = OrderFinancialProfile(
            order_value=order_value,
            product_category=product_category,
            product_weight_grams=weight_grams,
            payment_method=payment_method,
        )
        cost_assessment: CostEngineAssessment = self.cost_engine.evaluate_order(financial_profile, prob)

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return OrderScoreResult(
            order_id=order_id,
            customer_id=customer_id,
            product_id=product_id,
            order_value=order_value,
            product_category=product_category,
            payment_method=payment_method,
            predicted_return_probability=round(prob, 4),
            risk_score=risk_score,
            risk_tier=risk_tier,
            risk_tier_name=risk_tier.value,
            gross_return_loss_inr=cost_assessment.gross_return_loss,
            unmitigated_expected_loss_inr=cost_assessment.unmitigated_expected_loss,
            recommended_action=cost_assessment.recommended_action,
            recommended_action_name=cost_assessment.recommended_action_name,
            expected_net_savings_inr=cost_assessment.expected_net_savings,
            mitigated_expected_loss_inr=cost_assessment.mitigated_expected_loss,
            action_rationale=cost_assessment.action_rationale,
            action_evaluations=[asdict(ae) for ae in cost_assessment.action_evaluations],
            scored_at=datetime.now().isoformat(),
            latency_ms=round(latency_ms, 3),
        )

    def score_batch(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        """High-throughput vectorized batch scoring for orders."""
        start_time = time.perf_counter()
        df_out = orders_df.copy()

        # Vectorized feature transformation and inference
        X = self.preprocessor.transform(df_out)
        X = np.ascontiguousarray(X, dtype=np.float32)
        probs = self.model.predict_proba(X)[:, 1]

        # Vectorized tier and score assignments
        df_out["predicted_return_probability"] = np.round(probs, 4)
        df_out["risk_score"] = np.round(probs * 100.0, 1)
        df_out["risk_tier"] = [self.tier_config.assign_tier(p).value for p in probs]

        # Financial loss evaluations
        gross_losses = []
        recommended_actions = []
        net_savings_list = []

        for (_, row), p in zip(df_out.iterrows(), probs):
            profile = OrderFinancialProfile(
                order_value=float(row.get("order_value", 2000.0)),
                product_category=str(row.get("product_category", "Clothing")),
                product_weight_grams=float(row.get("product_weight_grams", 1000.0)),
                payment_method=str(row.get("payment_method", "UPI")),
            )
            assessment = self.cost_engine.evaluate_order(profile, p)
            gross_losses.append(assessment.gross_return_loss)
            recommended_actions.append(assessment.recommended_action.value)
            net_savings_list.append(assessment.expected_net_savings)

        df_out["gross_return_loss_inr"] = gross_losses
        df_out["unmitigated_expected_loss_inr"] = np.round(df_out["predicted_return_probability"] * np.array(gross_losses), 2)
        df_out["recommended_action"] = recommended_actions
        df_out["expected_net_savings_inr"] = np.round(net_savings_list, 2)

        elapsed = time.perf_counter() - start_time
        logger.info(f"Scored batch of {len(orders_df):,} orders in {elapsed:.3f}s ({len(orders_df)/elapsed:,.0f} orders/sec).")
        return df_out
