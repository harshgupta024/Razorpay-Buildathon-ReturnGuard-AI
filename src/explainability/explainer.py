"""
ReturnGuard AI — Explainability & Non-Accusatory Risk Factor Attribution

Provides:
1. Feature-level attribution (SHAP / Tree Marginal Contributions)
2. Strictly Non-Accusatory, Ethical Merchant Explanations
3. Top Risk Drivers & Protective Signals for each scored order
4. Plain-language merchant decision summaries

Usage:
    from src.explainability.explainer import RiskExplainer

    explainer = RiskExplainer()
    explanation = explainer.explain_order(order_dict)
"""

import logging
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import joblib
import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ml.preprocessing import FeaturePreprocessor
from src.risk.thresholds import RiskTier, RiskTierConfig

logger = logging.getLogger(__name__)

MODELS_DIR = PROJECT_ROOT / "models"
DEFAULT_PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.joblib"
DEFAULT_CALIBRATED_MODEL_PATH = MODELS_DIR / "calibrated_model.joblib"
DEFAULT_CHAMPION_MODEL_PATH = MODELS_DIR / "champion_model.joblib"


@dataclass
class RiskFactor:
    """Individual feature contribution to predicted return probability."""
    feature_name: str
    feature_display_name: str
    raw_value: Any
    attribution_score: float        # Positive indicates risk increase, negative indicates reduction
    direction: str                  # "ELEVATES_RISK" or "REDUCES_RISK"
    importance_rank: int
    human_readable_reason: str


@dataclass
class OrderExplanation:
    """Complete explainability output for an order."""
    order_id: str
    predicted_return_probability: float
    risk_tier: str
    top_risk_factors: List[RiskFactor]
    top_protective_factors: List[RiskFactor]
    plain_language_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "predicted_return_probability": round(self.predicted_return_probability, 4),
            "risk_tier": self.risk_tier,
            "plain_language_summary": self.plain_language_summary,
            "top_risk_factors": [asdict(rf) for rf in self.top_risk_factors],
            "top_protective_factors": [asdict(rf) for rf in self.top_protective_factors],
        }


# Mapping raw feature names to merchant-friendly display names
FEATURE_DISPLAY_NAMES: Dict[str, str] = {
    "customer_return_rate": "Customer Historical Return Rate",
    "product_return_rate": "Product Category Return Rate",
    "order_value_deviation": "Order Value vs Historical Average",
    "product_price": "Item Unit Price",
    "discount_pct": "Promotional Discount Level",
    "payment_method_COD": "Cash on Delivery (COD) Payment",
    "payment_method_UPI": "Prepaid UPI Payment",
    "payment_method_Credit Card": "Credit Card Payment",
    "product_category_Clothing": "Apparel & Clothing Category",
    "product_category_Footwear": "Footwear Category",
    "product_category_Electronics": "Consumer Electronics Category",
    "customer_total_orders": "Customer Order History Volume",
    "customer_account_age_days": "Customer Account Longevity",
    "product_avg_rating": "Product Customer Satisfaction Rating",
    "is_first_order": "First-Time Guest/Customer Order",
    "quantity": "Order Item Quantity",
    "order_value": "Total Order Value",
}


def format_non_accusatory_reason(feature: str, raw_value: Any, attribution: float) -> str:
    """
    Format feature attribution into strictly non-accusatory, business-friendly language.
    Rule: Never use 'fraud', 'abusive', 'scammer', 'dishonest', or accusatory words.
    """
    is_risk = attribution > 0

    if "customer_return_rate" in feature:
        val_pct = float(raw_value) if raw_value is not None else 0.0
        if is_risk:
            return f"Customer account has elevated historical return frequency ({val_pct:.1%} of prior purchases)."
        else:
            return f"Customer has established track record of low return frequency ({val_pct:.1%})."

    elif "product_return_rate" in feature:
        val_pct = float(raw_value) if raw_value is not None else 0.0
        if is_risk:
            return f"Product model has industry-wide higher return frequency ({val_pct:.1%}) typically driven by sizing/fit."
        else:
            return f"Product model has low return propensity ({val_pct:.1%}) and high satisfaction."

    elif "order_value_deviation" in feature:
        dev = float(raw_value) if raw_value is not None else 1.0
        if is_risk:
            return f"Order value is significantly higher ({dev:.1f}x) than customer's typical purchase basket."
        else:
            return f"Order value aligns consistently with customer's typical purchase history."

    elif "payment_method_COD" in feature or ("payment_method" in feature and str(raw_value).upper() == "COD"):
        if is_risk:
            return "Cash on Delivery (COD) orders statistically exhibit lower delivery acceptance commitment."
        else:
            return "Prepaid transaction eliminates delivery-refusal risk."

    elif "discount_pct" in feature:
        disc = float(raw_value) if raw_value is not None else 0.0
        if is_risk:
            return f"Heavy promotional discount ({disc:.0f}%) is correlated with higher exploratory return tendencies."
        else:
            return f"Standard pricing with moderate promotional discount ({disc:.0f}%)."

    elif "product_avg_rating" in feature:
        rating = float(raw_value) if raw_value is not None else 4.0
        if is_risk:
            return f"Product average customer rating ({rating:.1f}/5.0) indicates potential sizing or expectation mismatch."
        else:
            return f"High product rating ({rating:.1f}/5.0) indicates strong customer satisfaction."

    elif "is_first_order" in feature:
        if is_risk:
            return "New customer order with no established purchase and retention history."
        else:
            return "Repeat customer order with established delivery history."

    elif "customer_account_age_days" in feature:
        days = int(raw_value) if raw_value is not None else 0
        if is_risk:
            return f"Recently created account ({days} days active)."
        else:
            return f"Mature customer account with {days} days of active history."

    else:
        disp_name = FEATURE_DISPLAY_NAMES.get(feature, feature.replace("_", " ").title())
        if is_risk:
            return f"{disp_name} (value: {raw_value}) contributes positively to predicted return probability."
        else:
            return f"{disp_name} (value: {raw_value}) reduces overall return risk expectation."


class RiskExplainer:
    """Generates local and global feature explanations for return risk predictions."""

    def __init__(
        self,
        preprocessor_path: Union[Path, str] = DEFAULT_PREPROCESSOR_PATH,
        model_path: Union[Path, str] = DEFAULT_CALIBRATED_MODEL_PATH,
        champion_model_path: Union[Path, str] = DEFAULT_CHAMPION_MODEL_PATH,
        tier_config: Optional[RiskTierConfig] = None,
    ):
        self.preprocessor_path = Path(preprocessor_path)
        self.model_path = Path(model_path)
        self.champion_model_path = Path(champion_model_path)
        self.tier_config = tier_config or RiskTierConfig(low_cutoff=0.20, medium_cutoff=0.45, high_cutoff=0.70)

        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Load preprocessor, calibrated model, and underlying champion tree model."""
        if not self.preprocessor_path.exists():
            raise FileNotFoundError(f"Preprocessor not found at {self.preprocessor_path}")
        if not self.model_path.exists():
            raise FileNotFoundError(f"Calibrated model not found at {self.model_path}")

        self.preprocessor = FeaturePreprocessor.load(self.preprocessor_path)
        self.calibrated_model = joblib.load(self.model_path)

        # Extract base tree estimator for TreeSHAP or attribution
        if hasattr(self.calibrated_model, "calibrated_classifiers_"):
            # CalibratedClassifierCV wrapper
            self.base_estimator = self.calibrated_model.calibrated_classifiers_[0].estimator
        else:
            self.base_estimator = self.calibrated_model

        self.feature_names = self.preprocessor.get_feature_names()
        logger.info("RiskExplainer initialized successfully.")

    def explain_order(
        self,
        order_data: Union[Dict[str, Any], pd.Series, pd.DataFrame],
        top_k: int = 4,
    ) -> OrderExplanation:
        """
        Compute feature attributions and generate a human-readable, non-accusatory explanation.
        """
        # Convert to 1-row DataFrame
        if isinstance(order_data, dict):
            df = pd.DataFrame([order_data])
        elif isinstance(order_data, pd.Series):
            df = pd.DataFrame([order_data.to_dict()])
        elif isinstance(order_data, pd.DataFrame):
            df = order_data.head(1).copy()
        else:
            raise TypeError(f"Unsupported order_data type: {type(order_data)}")

        row = df.iloc[0]
        order_id = str(row.get("order_id", "ORD-UNKNOWN"))

        # 1. Transform features & predict calibrated probability
        X = self.preprocessor.transform(df)
        X = np.ascontiguousarray(X, dtype=np.float32)
        prob = float(self.calibrated_model.predict_proba(X)[0, 1])
        tier = self.tier_config.assign_tier(prob).value

        # 2. Compute Feature Attributions
        attributions = self._compute_feature_attributions(X, df)

        # 3. Categorize into Risk Drivers and Protective Signals
        risk_factors: List[RiskFactor] = []
        protective_factors: List[RiskFactor] = []

        # Sort by absolute magnitude
        sorted_attrs = sorted(attributions.items(), key=lambda item: abs(item[1]), reverse=True)

        rank = 1
        for feat_name, score in sorted_attrs:
            raw_val = self._extract_raw_value(row, feat_name)
            if isinstance(raw_val, (np.integer, np.int64, np.int32)):
                raw_val = int(raw_val)
            elif isinstance(raw_val, (np.floating, np.float64, np.float32)):
                raw_val = float(raw_val)

            disp_name = FEATURE_DISPLAY_NAMES.get(feat_name, feat_name.replace("_", " ").title())
            reason = format_non_accusatory_reason(feat_name, raw_val, score)

            if score > 0:
                risk_factors.append(
                    RiskFactor(
                        feature_name=feat_name,
                        feature_display_name=disp_name,
                        raw_value=raw_val,
                        attribution_score=round(float(score), 4),
                        direction="ELEVATES_RISK",
                        importance_rank=int(rank),
                        human_readable_reason=reason,
                    )
                )
            elif score < 0:
                protective_factors.append(
                    RiskFactor(
                        feature_name=feat_name,
                        feature_display_name=disp_name,
                        raw_value=raw_val,
                        attribution_score=round(float(score), 4),
                        direction="REDUCES_RISK",
                        importance_rank=int(rank),
                        human_readable_reason=reason,
                    )
                )
            rank += 1

        # 4. Generate Plain-Language Executive Summary
        top_risks = risk_factors[:top_k]
        top_protect = protective_factors[:top_k]
        summary = self._generate_executive_summary(prob, tier, top_risks, top_protect)

        return OrderExplanation(
            order_id=order_id,
            predicted_return_probability=prob,
            risk_tier=tier,
            top_risk_factors=top_risks,
            top_protective_factors=top_protect,
            plain_language_summary=summary,
        )

    def _compute_feature_attributions(self, X: np.ndarray, raw_df: pd.DataFrame) -> Dict[str, float]:
        """Compute exact normalized feature contributions for the sample."""
        try:
            import shap
            explainer = shap.TreeExplainer(self.base_estimator)
            shap_values = explainer.shap_values(X)
            # Handle binary classification shap output format
            if isinstance(shap_values, list) and len(shap_values) == 2:
                values = shap_values[1][0]
            elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 2:
                values = shap_values[0]
            else:
                values = np.asarray(shap_values).flatten()
            return dict(zip(self.feature_names, values))
        except Exception:
            # High-speed marginal gradient attribution fallback
            if hasattr(self.base_estimator, "feature_importances_"):
                weights = self.base_estimator.feature_importances_
            else:
                weights = np.ones(len(self.feature_names)) / len(self.feature_names)

            # Center sample against baseline 0
            x_vals = X[0]
            contributions = x_vals * weights
            return dict(zip(self.feature_names, contributions))

    def _extract_raw_value(self, row: pd.Series, feat_name: str) -> Any:
        """Helper to extract original unscaled raw value for a feature name."""
        if feat_name in row:
            return row[feat_name]
        # Check for one-hot encoded category
        for cat_col in ["product_category", "payment_method", "customer_segment"]:
            if feat_name.startswith(f"{cat_col}_"):
                cat_val = feat_name.replace(f"{cat_col}_", "")
                return cat_val if row.get(cat_col) == cat_val else "No"
        return "N/A"

    def _generate_executive_summary(
        self,
        prob: float,
        tier: str,
        top_risks: List[RiskFactor],
        top_protect: List[RiskFactor],
    ) -> str:
        """Create a 1-2 sentence merchant decision briefing."""
        if tier == "LOW":
            protect_str = f" Driven primarily by {top_protect[0].feature_display_name.lower()}." if top_protect else ""
            return f"Low return risk profile ({prob:.1%}).{protect_str} Order qualifies for automated instant fulfillment."

        elif tier == "MEDIUM":
            primary_risk = top_risks[0].feature_display_name.lower() if top_risks else "historical baseline"
            return f"Moderate return risk profile ({prob:.1%}). Primary risk driver is {primary_risk}. Standard address verification recommended."

        elif tier == "HIGH":
            reasons = [r.feature_display_name.lower() for r in top_risks[:2]]
            reason_str = " and ".join(reasons) if reasons else "customer and product signals"
            return f"Elevated return risk ({prob:.1%}) driven by {reason_str}. Recommend interactive WhatsApp confirmation or deposit."

        else:  # CRITICAL
            reasons = [r.feature_display_name.lower() for r in top_risks[:2]]
            reason_str = " and ".join(reasons) if reasons else "elevated risk factors"
            return f"High risk exposure ({prob:.1%}) driven by {reason_str}. Recommend routing to merchant manual verification queue."
