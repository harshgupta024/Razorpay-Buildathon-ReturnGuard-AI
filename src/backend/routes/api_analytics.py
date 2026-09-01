"""
ReturnGuard AI — Merchant Analytics & Portfolio Intelligence (/api/v1/analytics)
"""

from collections import Counter
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.backend.schemas import AnalyticsSummaryResponse
from src.db.session import OrderRecord, RiskAssessmentRecord, get_db

router = APIRouter(prefix="/api/v1/analytics", tags=["Portfolio Analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse, status_code=status.HTTP_200_OK)
def get_analytics_summary(db: Session = Depends(get_db)):
    """Compute real-time aggregate risk exposure, projected savings, and category return metrics."""
    assessments = db.query(RiskAssessmentRecord).all()
    orders = db.query(OrderRecord).all()

    total_orders = len(assessments)
    if total_orders == 0:
        return AnalyticsSummaryResponse(
            total_orders_analyzed=0,
            total_portfolio_value_inr=0.0,
            total_unmitigated_risk_exposure_inr=0.0,
            total_projected_net_savings_inr=0.0,
            portfolio_avg_return_probability=0.0,
            tier_distribution={"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
            tier_proportions={"LOW": 0.0, "MEDIUM": 0.0, "HIGH": 0.0, "CRITICAL": 0.0},
            category_breakdown=[],
            recommended_actions_breakdown={},
        )

    total_portfolio_val = sum(o.order_value for o in orders)
    total_unmitigated_exposure = sum(a.unmitigated_expected_loss_inr for a in assessments)
    total_savings = sum(a.expected_net_savings_inr for a in assessments)
    avg_prob = sum(a.predicted_return_probability for a in assessments) / total_orders

    tier_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    action_counts = Counter()

    for a in assessments:
        t = a.risk_tier.upper()
        if t in tier_counts:
            tier_counts[t] += 1
        else:
            tier_counts[t] = 1
        action_counts[a.recommended_action] += 1

    tier_props = {k: round(v / total_orders, 4) for k, v in tier_counts.items()}

    # Category breakdown
    cat_map = {}
    order_dict_by_id = {o.order_id: o for o in orders}
    for a in assessments:
        o = order_dict_by_id.get(a.order_id)
        if o:
            cat = o.product_category
            if cat not in cat_map:
                cat_map[cat] = {"category": cat, "orders": 0, "total_value": 0.0, "prob_sum": 0.0, "savings_sum": 0.0}
            cat_map[cat]["orders"] += 1
            cat_map[cat]["total_value"] += o.order_value
            cat_map[cat]["prob_sum"] += a.predicted_return_probability
            cat_map[cat]["savings_sum"] += a.expected_net_savings_inr

    cat_breakdown = []
    for c in cat_map.values():
        cat_breakdown.append({
            "category": c["category"],
            "order_count": c["orders"],
            "total_value_inr": round(c["total_value"], 2),
            "avg_return_risk": round(c["prob_sum"] / c["orders"], 4) if c["orders"] > 0 else 0.0,
            "projected_savings_inr": round(c["savings_sum"], 2),
        })

    cat_breakdown.sort(key=lambda x: x["order_count"], reverse=True)

    return AnalyticsSummaryResponse(
        total_orders_analyzed=total_orders,
        total_portfolio_value_inr=round(total_portfolio_val, 2),
        total_unmitigated_risk_exposure_inr=round(total_unmitigated_exposure, 2),
        total_projected_net_savings_inr=round(total_savings, 2),
        portfolio_avg_return_probability=round(avg_prob, 4),
        tier_distribution=tier_counts,
        tier_proportions=tier_props,
        category_breakdown=cat_breakdown,
        recommended_actions_breakdown=dict(action_counts),
    )
