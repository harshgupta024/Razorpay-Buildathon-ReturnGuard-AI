"""
ReturnGuard AI — Business Cost & Financial Simulation Engine

Provides order-specific and portfolio-level financial loss calculations,
mitigation action cost-benefit simulations, and dynamic ROI projections.

Key Concepts:
1. Gross Return Loss = Forward Shipping + Return Shipping + Restocking + Depreciation + Packaging
2. Expected Loss = P(Return) * Gross Return Loss
3. Mitigation Policy Evaluation = Expected Savings vs Friction Cost
4. Optimal Action Recommendation maximizing merchant Net Profit

Usage:
    from src.business.cost_engine import BusinessCostEngine, OrderFinancialProfile
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np


class MitigationActionType(str, Enum):
    ALLOW_SEAMLESS = "ALLOW_SEAMLESS"
    SOFT_CONFIRMATION = "SOFT_CONFIRMATION"
    WHATSAPP_CONFIRMATION = "WHATSAPP_CONFIRMATION"
    REQUIRE_PREPAID_OR_DEPOSIT = "REQUIRE_PREPAID_OR_DEPOSIT"
    MANUAL_REVIEW_CALL = "MANUAL_REVIEW_CALL"


@dataclass
class MitigationPolicy:
    """Attributes and expected efficacy of a merchant intervention."""
    action_type: MitigationActionType
    display_name: str
    description: str
    action_cost_inr: float          # Direct technical/operational cost (e.g. WhatsApp API, OTP, staff)
    friction_cost_inr: float        # Expected customer drop-off / conversion penalty
    return_reduction_rate: float    # Expected % reduction in return likelihood (0.0 to 1.0)


# Standard Industry Mitigation Policies
DEFAULT_MITIGATION_POLICIES: Dict[MitigationActionType, MitigationPolicy] = {
    MitigationActionType.ALLOW_SEAMLESS: MitigationPolicy(
        action_type=MitigationActionType.ALLOW_SEAMLESS,
        display_name="1-Click Seamless Checkout",
        description="Friction-free instant checkout. Ideal for low-risk purchases.",
        action_cost_inr=0.0,
        friction_cost_inr=0.0,
        return_reduction_rate=0.0,
    ),
    MitigationActionType.SOFT_CONFIRMATION: MitigationPolicy(
        action_type=MitigationActionType.SOFT_CONFIRMATION,
        display_name="Soft Engagement & Address Verification",
        description="In-app address validation popup and return policy notification.",
        action_cost_inr=2.0,
        friction_cost_inr=5.0,
        return_reduction_rate=0.15,
    ),
    MitigationActionType.WHATSAPP_CONFIRMATION: MitigationPolicy(
        action_type=MitigationActionType.WHATSAPP_CONFIRMATION,
        display_name="Interactive WhatsApp Order & Size Confirmation",
        description="Automated WhatsApp prompt asking buyer to confirm sizing and delivery availability.",
        action_cost_inr=5.0,
        friction_cost_inr=15.0,
        return_reduction_rate=0.40,
    ),
    MitigationActionType.REQUIRE_PREPAID_OR_DEPOSIT: MitigationPolicy(
        action_type=MitigationActionType.REQUIRE_PREPAID_OR_DEPOSIT,
        display_name="Require Partial Deposit or UPI/Card Prepayment",
        description="Restricts pure COD by requiring Rs. 100 advance shipping deposit or prepaid payment.",
        action_cost_inr=0.0,
        friction_cost_inr=45.0,
        return_reduction_rate=0.70,
    ),
    MitigationActionType.MANUAL_REVIEW_CALL: MitigationPolicy(
        action_type=MitigationActionType.MANUAL_REVIEW_CALL,
        display_name="Manual Verification Queue & Support Call",
        description="Routes critical order to merchant review queue for proactive customer phone verification.",
        action_cost_inr=40.0,
        friction_cost_inr=30.0,
        return_reduction_rate=0.85,
    ),
}


# Category-specific restocking depreciation rates
CATEGORY_DEPRECIATION_RATES: Dict[str, float] = {
    "Electronics": 0.12,   # Open-box markdown & repackaging
    "Clothing": 0.18,      # Seasonal fashion depreciation & dry cleaning
    "Footwear": 0.15,      # Box damage & minor wear inspection
    "Beauty": 0.25,        # Hygiene seals broken / unsellable
    "Home": 0.10,          # Furniture / decor handling
    "Books": 0.05,         # Resellable with minimal wear
    "Sports": 0.10,        # Gear inspection
    "Accessories": 0.12,   # Packaging replacement
}


@dataclass
class OrderFinancialProfile:
    """Financial breakdown and return cost structure for an order."""
    order_value: float
    product_category: str
    product_weight_grams: float = 1000.0
    payment_method: str = "UPI"
    forward_shipping_cost: float = 100.0
    return_shipping_cost: float = 150.0
    restocking_inspection_cost: float = 80.0
    packaging_loss_cost: float = 40.0
    depreciation_rate: Optional[float] = None

    def __post_init__(self):
        if self.depreciation_rate is None:
            self.depreciation_rate = CATEGORY_DEPRECIATION_RATES.get(self.product_category, 0.12)
        # Weight-based reverse logistics surcharge (>2kg)
        if self.product_weight_grams > 2000.0:
            extra_kg = (self.product_weight_grams - 2000.0) / 1000.0
            self.return_shipping_cost += float(extra_kg * 40.0)

    @property
    def product_depreciation_loss(self) -> float:
        """Expected monetary loss from product value depreciation upon return."""
        return float(self.order_value * self.depreciation_rate)

    @property
    def gross_return_loss(self) -> float:
        """Total direct financial loss incurred by the merchant if this order is returned."""
        return float(
            self.forward_shipping_cost
            + self.return_shipping_cost
            + self.restocking_inspection_cost
            + self.packaging_loss_cost
            + self.product_depreciation_loss
        )


@dataclass
class ActionEvaluation:
    """Cost-benefit evaluation of a single candidate mitigation policy."""
    action_type: MitigationActionType
    display_name: str
    expected_residual_loss: float
    total_intervention_cost: float
    total_expected_cost: float
    expected_net_savings: float
    is_recommended: bool = False


@dataclass
class CostEngineAssessment:
    """Complete financial risk & mitigation assessment for an order."""
    order_value: float
    predicted_return_probability: float
    gross_return_loss: float
    unmitigated_expected_loss: float
    recommended_action: MitigationActionType
    recommended_action_name: str
    expected_net_savings: float
    mitigated_expected_loss: float
    action_evaluations: List[ActionEvaluation]
    action_rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_value": round(self.order_value, 2),
            "predicted_return_probability": round(self.predicted_return_probability, 4),
            "gross_return_loss": round(self.gross_return_loss, 2),
            "unmitigated_expected_loss": round(self.unmitigated_expected_loss, 2),
            "recommended_action": self.recommended_action.value,
            "recommended_action_name": self.recommended_action_name,
            "expected_net_savings": round(self.expected_net_savings, 2),
            "mitigated_expected_loss": round(self.mitigated_expected_loss, 2),
            "action_rationale": self.action_rationale,
            "action_evaluations": [
                {
                    "action_type": ae.action_type.value,
                    "display_name": ae.display_name,
                    "expected_residual_loss": round(ae.expected_residual_loss, 2),
                    "total_intervention_cost": round(ae.total_intervention_cost, 2),
                    "total_expected_cost": round(ae.total_expected_cost, 2),
                    "expected_net_savings": round(ae.expected_net_savings, 2),
                    "is_recommended": ae.is_recommended,
                }
                for ae in self.action_evaluations
            ],
        }


class BusinessCostEngine:
    """Evaluates expected return financial losses and recommends profit-maximizing actions."""

    def __init__(
        self,
        policies: Optional[Dict[MitigationActionType, MitigationPolicy]] = None,
    ):
        self.policies = policies or DEFAULT_MITIGATION_POLICIES

    def evaluate_order(
        self,
        order_profile: OrderFinancialProfile,
        return_probability: float,
    ) -> CostEngineAssessment:
        """
        Compute financial loss expectations and select the optimal mitigation action.
        """
        p = float(np.clip(return_probability, 0.0, 1.0))
        gross_loss = order_profile.gross_return_loss
        unmitigated_loss = p * gross_loss

        evaluations: List[ActionEvaluation] = []

        for action_type, policy in self.policies.items():
            # Residual probability after mitigation intervention
            p_residual = p * (1.0 - policy.return_reduction_rate)
            expected_residual_loss = p_residual * gross_loss
            intervention_cost = policy.action_cost_inr + policy.friction_cost_inr
            total_cost = expected_residual_loss + intervention_cost
            net_savings = unmitigated_loss - total_cost

            evaluations.append(
                ActionEvaluation(
                    action_type=action_type,
                    display_name=policy.display_name,
                    expected_residual_loss=expected_residual_loss,
                    total_intervention_cost=intervention_cost,
                    total_expected_cost=total_cost,
                    expected_net_savings=net_savings,
                )
            )

        # Select action that maximizes net savings (or lowest total expected cost)
        best_eval = max(evaluations, key=lambda e: e.expected_net_savings)
        best_eval.is_recommended = True

        # Synthesize clear, non-accusatory merchant rationale
        rationale = self._generate_rationale(order_profile, p, best_eval, gross_loss)

        return CostEngineAssessment(
            order_value=order_profile.order_value,
            predicted_return_probability=p,
            gross_return_loss=gross_loss,
            unmitigated_expected_loss=unmitigated_loss,
            recommended_action=best_eval.action_type,
            recommended_action_name=best_eval.display_name,
            expected_net_savings=max(0.0, best_eval.expected_net_savings),
            mitigated_expected_loss=best_eval.total_expected_cost,
            action_evaluations=evaluations,
            action_rationale=rationale,
        )

    def _generate_rationale(
        self,
        profile: OrderFinancialProfile,
        p: float,
        best_eval: ActionEvaluation,
        gross_loss: float,
    ) -> str:
        """Generate plain-language financial justification for the recommended mitigation."""
        if best_eval.action_type == MitigationActionType.ALLOW_SEAMLESS:
            return (
                f"Low expected return likelihood ({p:.1%}). Estimated return loss of ₹{p * gross_loss:.0f} "
                f"is negligible. Seamless 1-click fulfillment recommended."
            )
        elif best_eval.action_type == MitigationActionType.SOFT_CONFIRMATION:
            return (
                f"Moderate return likelihood ({p:.1%}). Soft address verification and return window "
                f"notice protects ₹{best_eval.expected_net_savings:.0f} with minimal checkout friction."
            )
        elif best_eval.action_type == MitigationActionType.WHATSAPP_CONFIRMATION:
            return (
                f"Elevated return likelihood ({p:.1%}) on ₹{profile.order_value:,.0f} {profile.product_category} order. "
                f"Interactive WhatsApp size & delivery confirmation delivers ₹{best_eval.expected_net_savings:.0f} net savings."
            )
        elif best_eval.action_type == MitigationActionType.REQUIRE_PREPAID_OR_DEPOSIT:
            return (
                f"High return risk ({p:.1%}) on COD purchase. Securing a ₹100 advance deposit or prepaid payment "
                f"avoids ₹{best_eval.expected_net_savings:.0f} in forward/reverse logistics loss."
            )
        else:
            return (
                f"Critical return risk ({p:.1%}) with high gross loss exposure (₹{gross_loss:,.0f}). "
                f"Dedicated phone verification queue avoids ₹{best_eval.expected_net_savings:.0f} in net operational loss."
            )
