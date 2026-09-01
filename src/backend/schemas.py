"""
ReturnGuard AI — FastAPI Pydantic Request & Response Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OrderInput(BaseModel):
    """Input payload for scoring a single order."""
    order_id: Optional[str] = Field(default=None, description="Unique Order ID (generated if empty)")
    customer_id: str = Field(default="CUST-0001", description="Customer unique ID")
    product_id: str = Field(default="PROD-0001", description="Product unique ID")
    order_value: float = Field(default=2499.0, ge=1.0, description="Order total in INR")
    product_category: str = Field(default="Clothing", description="Product category")
    payment_method: str = Field(default="COD", description="Payment method: UPI, Credit Card, Debit Card, Net Banking, COD")
    quantity: int = Field(default=1, ge=1, description="Quantity of items")
    discount_pct: float = Field(default=15.0, ge=0.0, le=100.0, description="Promotional discount %")
    is_first_order: int = Field(default=0, ge=0, le=1, description="1 if guest/first order, 0 if repeat")
    customer_account_age_days: int = Field(default=120, ge=0, description="Days since customer account creation")
    customer_total_orders: int = Field(default=4, ge=1, description="Customer historical total orders")
    customer_total_returns: int = Field(default=1, ge=0, description="Customer historical total returns")
    customer_return_rate: float = Field(default=0.25, ge=0.0, le=1.0, description="Customer historical return rate")
    customer_avg_order_value: float = Field(default=2200.0, ge=0.0, description="Customer average order value")
    customer_days_since_last_order: int = Field(default=14, ge=0, description="Days since previous order")
    customer_segment: str = Field(default="regular", description="Customer tier: new, regular, premium, vip")
    product_price: float = Field(default=2499.0, ge=1.0, description="Product base price")
    product_weight_grams: float = Field(default=850.0, ge=10.0, description="Product weight in grams")
    product_return_rate: float = Field(default=0.28, ge=0.0, le=1.0, description="Product model return rate")
    product_avg_rating: float = Field(default=4.2, ge=1.0, le=5.0, description="Product rating")
    order_value_deviation: float = Field(default=1.13, ge=0.0, description="order_value / customer_avg_order_value")
    order_hour: int = Field(default=14, ge=0, le=23, description="Hour of order (0-23)")
    order_day_of_week: int = Field(default=2, ge=0, le=6, description="Day of week (0=Mon, 6=Sun)")
    is_weekend_order: int = Field(default=0, ge=0, le=1, description="1 if Sat/Sun, else 0")


class BatchOrderInput(BaseModel):
    """Input payload for batch order scoring."""
    orders: List[OrderInput] = Field(..., description="List of orders to score")


class RiskFactorSchema(BaseModel):
    """Attribution detail for a single feature."""
    feature_name: str
    feature_display_name: str
    raw_value: Any
    attribution_score: float
    direction: str
    importance_rank: int
    human_readable_reason: str


class ActionEvaluationSchema(BaseModel):
    """Cost-benefit metrics for a candidate mitigation policy."""
    action_type: str
    display_name: str
    expected_residual_loss: float
    total_intervention_cost: float
    total_expected_cost: float
    expected_net_savings: float
    is_recommended: bool


class OrderScoreResponse(BaseModel):
    """Complete prediction and decision response for an order."""
    order_id: str
    customer_id: str
    product_id: str
    order_value: float
    product_category: str
    payment_method: str
    predicted_return_probability: float
    risk_score: float
    risk_tier: str
    gross_return_loss_inr: float
    unmitigated_expected_loss_inr: float
    recommended_action: str
    recommended_action_name: str
    expected_net_savings_inr: float
    mitigated_expected_loss_inr: float
    action_rationale: str
    action_evaluations: List[ActionEvaluationSchema]
    top_risk_factors: List[RiskFactorSchema]
    top_protective_factors: List[RiskFactorSchema]
    plain_language_summary: str
    scored_at: str
    latency_ms: float


class BatchScoreResponse(BaseModel):
    """Response payload for batch order scoring."""
    total_orders_scored: int
    total_expected_loss_inr: float
    total_expected_net_savings_inr: float
    results: List[OrderScoreResponse]


class ReviewDecisionRequest(BaseModel):
    """Merchant decision payload for human review."""
    decision: str = Field(..., description="Decision: APPROVED_SEAMLESS, REQUIRED_DEPOSIT, REQUIRED_WHATSAPP, CANCELLED")
    notes: Optional[str] = Field(default="", description="Merchant review notes or reason")
    reviewer_id: Optional[str] = Field(default="merchant_admin", description="ID of staff member submitting review")


class ReviewDecisionResponse(BaseModel):
    """Confirmation of review submission."""
    order_id: str
    decision: str
    status: str
    reviewed_at: str
    message: str


class AnalyticsSummaryResponse(BaseModel):
    """High-level merchant financial & risk summary."""
    total_orders_analyzed: int
    total_portfolio_value_inr: float
    total_unmitigated_risk_exposure_inr: float
    total_projected_net_savings_inr: float
    portfolio_avg_return_probability: float
    tier_distribution: Dict[str, int]
    tier_proportions: Dict[str, float]
    category_breakdown: List[Dict[str, Any]]
    recommended_actions_breakdown: Dict[str, int]


class ThresholdPresetResponse(BaseModel):
    """Current threshold configuration and available strategy presets."""
    active_preset: str
    active_cutoffs: Dict[str, float]
    available_presets: Dict[str, Any]


class HealthResponse(BaseModel):
    """Service health status."""
    model_config = {"protected_namespaces": ()}

    status: str
    app_name: str
    model_version: str
    model_calibrated: bool
    timestamp: str
