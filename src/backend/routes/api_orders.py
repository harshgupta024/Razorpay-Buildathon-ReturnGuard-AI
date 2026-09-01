"""
ReturnGuard AI — Orders Feed Endpoints (/api/v1/orders)
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.db.session import OrderRecord, RiskAssessmentRecord, ReviewRecord, get_db

router = APIRouter(prefix="/api/v1/orders", tags=["Orders & Historical Feed"])


@router.get("", status_code=status.HTTP_200_OK)
def list_orders(
    tier: Optional[str] = Query(None, description="Filter by risk tier (LOW, MEDIUM, HIGH, CRITICAL)"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Retrieve scored orders with risk assessments and review status."""
    query = db.query(OrderRecord).join(RiskAssessmentRecord, OrderRecord.order_id == RiskAssessmentRecord.order_id)

    if tier:
        query = query.filter(RiskAssessmentRecord.risk_tier == tier.upper())
    if category:
        query = query.filter(OrderRecord.product_category == category)
    if payment_method:
        query = query.filter(OrderRecord.payment_method == payment_method)

    total_count = query.count()
    orders = query.order_by(OrderRecord.created_at.desc()).offset(offset).limit(limit).all()

    items = []
    for o in orders:
        items.append({
            "order_id": o.order_id,
            "customer_id": o.customer_id,
            "product_id": o.product_id,
            "order_value": o.order_value,
            "product_category": o.product_category,
            "payment_method": o.payment_method,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "assessment": {
                "predicted_return_probability": o.assessment.predicted_return_probability if o.assessment else None,
                "risk_score": o.assessment.risk_score if o.assessment else None,
                "risk_tier": o.assessment.risk_tier if o.assessment else None,
                "recommended_action": o.assessment.recommended_action if o.assessment else None,
                "recommended_action_name": o.assessment.recommended_action_name if o.assessment else None,
                "expected_net_savings_inr": o.assessment.expected_net_savings_inr if o.assessment else 0.0,
                "unmitigated_expected_loss_inr": o.assessment.unmitigated_expected_loss_inr if o.assessment else 0.0,
                "plain_language_summary": o.assessment.plain_language_summary if o.assessment else None,
            } if o.assessment else None,
            "review": {
                "decision": o.review.decision,
                "is_overridden": o.review.is_overridden,
                "notes": o.review.notes,
                "reviewed_at": o.review.reviewed_at.isoformat() if o.review.reviewed_at else None,
            } if o.review else None,
        })

    return {
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "orders": items,
    }


@router.get("/{order_id}", status_code=status.HTTP_200_OK)
def get_order_detail(
    order_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve full details, explainability factors, and review audit trail for a single order."""
    order = db.query(OrderRecord).filter_by(order_id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")

    return {
        "order_id": order.order_id,
        "customer_id": order.customer_id,
        "product_id": order.product_id,
        "order_value": order.order_value,
        "product_category": order.product_category,
        "payment_method": order.payment_method,
        "quantity": order.quantity,
        "discount_pct": order.discount_pct,
        "customer_account_age_days": order.customer_account_age_days,
        "customer_total_orders": order.customer_total_orders,
        "customer_total_returns": order.customer_total_returns,
        "customer_return_rate": order.customer_return_rate,
        "product_price": order.product_price,
        "product_return_rate": order.product_return_rate,
        "order_value_deviation": order.order_value_deviation,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "assessment": {
            "predicted_return_probability": order.assessment.predicted_return_probability,
            "risk_score": order.assessment.risk_score,
            "risk_tier": order.assessment.risk_tier,
            "gross_return_loss_inr": order.assessment.gross_return_loss_inr,
            "unmitigated_expected_loss_inr": order.assessment.unmitigated_expected_loss_inr,
            "recommended_action": order.assessment.recommended_action,
            "recommended_action_name": order.assessment.recommended_action_name,
            "expected_net_savings_inr": order.assessment.expected_net_savings_inr,
            "mitigated_expected_loss_inr": order.assessment.mitigated_expected_loss_inr,
            "action_rationale": order.assessment.action_rationale,
            "plain_language_summary": order.assessment.plain_language_summary,
            "top_risk_factors": order.assessment.top_risk_factors,
            "top_protective_factors": order.assessment.top_protective_factors,
            "scored_at": order.assessment.scored_at.isoformat() if order.assessment.scored_at else None,
            "latency_ms": order.assessment.latency_ms,
        } if order.assessment else None,
        "review": {
            "decision": order.review.decision,
            "is_overridden": order.review.is_overridden,
            "notes": order.review.notes,
            "reviewer_id": order.review.reviewer_id,
            "reviewed_at": order.review.reviewed_at.isoformat() if order.review.reviewed_at else None,
        } if order.review else None,
        "audit_logs": [
            {
                "event_type": al.event_type,
                "actor": al.actor,
                "payload": al.payload,
                "timestamp": al.timestamp.isoformat() if al.timestamp else None,
            }
            for al in order.audit_logs
        ],
    }
