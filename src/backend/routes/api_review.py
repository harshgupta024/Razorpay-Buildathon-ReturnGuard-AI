"""
ReturnGuard AI — Human-in-the-Loop Review Queue Endpoints (/api/v1/review)
Phase 15 Implementation
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.schemas import ReviewDecisionRequest, ReviewDecisionResponse
from src.db.session import AuditLogRecord, OrderRecord, ReviewRecord, RiskAssessmentRecord, get_db

router = APIRouter(prefix="/api/v1/review", tags=["Human-in-the-Loop Review Queue"])


@router.get("/queue", status_code=status.HTTP_200_OK)
def get_review_queue(
    status_filter: str = Query("PENDING", description="Filter by status: PENDING, REVIEWED, ALL"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Retrieve orders flagged in HIGH or CRITICAL risk tiers requiring merchant review.
    """
    query = (
        db.query(OrderRecord)
        .join(RiskAssessmentRecord, OrderRecord.order_id == RiskAssessmentRecord.order_id)
        .outerjoin(ReviewRecord, OrderRecord.order_id == ReviewRecord.order_id)
        .filter(RiskAssessmentRecord.risk_tier.in_(["HIGH", "CRITICAL"]))
    )

    if status_filter.upper() == "PENDING":
        query = query.filter(ReviewRecord.id == None)  # Not yet reviewed
    elif status_filter.upper() == "REVIEWED":
        query = query.filter(ReviewRecord.id != None)  # Already reviewed

    total_pending = query.count()
    orders = query.order_by(RiskAssessmentRecord.predicted_return_probability.desc()).offset(offset).limit(limit).all()

    queue_items = []
    for o in orders:
        queue_items.append({
            "order_id": o.order_id,
            "customer_id": o.customer_id,
            "product_id": o.product_id,
            "order_value": o.order_value,
            "product_category": o.product_category,
            "payment_method": o.payment_method,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "risk_score": o.assessment.risk_score if o.assessment else 0.0,
            "predicted_return_probability": o.assessment.predicted_return_probability if o.assessment else 0.0,
            "risk_tier": o.assessment.risk_tier if o.assessment else "UNKNOWN",
            "recommended_action": o.assessment.recommended_action if o.assessment else "N/A",
            "recommended_action_name": o.assessment.recommended_action_name if o.assessment else "N/A",
            "gross_return_loss_inr": o.assessment.gross_return_loss_inr if o.assessment else 0.0,
            "expected_net_savings_inr": o.assessment.expected_net_savings_inr if o.assessment else 0.0,
            "plain_language_summary": o.assessment.plain_language_summary if o.assessment else None,
            "top_risk_factors": o.assessment.top_risk_factors if o.assessment else [],
            "review_status": "REVIEWED" if o.review else "PENDING",
            "review_decision": o.review.decision if o.review else None,
            "review_notes": o.review.notes if o.review else None,
            "reviewed_at": o.review.reviewed_at.isoformat() if (o.review and o.review.reviewed_at) else None,
        })

    return {
        "total_queue_count": total_pending,
        "status_filter": status_filter.upper(),
        "queue": queue_items,
    }


@router.post("/{order_id}/decision", response_model=ReviewDecisionResponse, status_code=status.HTTP_200_OK)
def submit_review_decision(
    order_id: str,
    payload: ReviewDecisionRequest,
    db: Session = Depends(get_db),
):
    """
    Submit a human merchant review decision / override:
    - Records decision, notes, and reviewer ID in reviews table
    - Appends immutable event to audit_logs table
    - Confirms override status
    """
    order = db.query(OrderRecord).filter_by(order_id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")

    original_tier = order.assessment.risk_tier if order.assessment else "UNKNOWN"
    original_action = order.assessment.recommended_action if order.assessment else "ALLOW_SEAMLESS"

    # Check if this decision overrides the automated recommended action
    is_override = (payload.decision.upper() != original_action.upper())

    existing_review = db.query(ReviewRecord).filter_by(order_id=order_id).first()
    if existing_review:
        existing_review.decision = payload.decision
        existing_review.notes = payload.notes
        existing_review.reviewer_id = payload.reviewer_id
        existing_review.reviewed_at = datetime.utcnow()
        existing_review.is_overridden = is_override
    else:
        new_review = ReviewRecord(
            order_id=order_id,
            original_risk_tier=original_tier,
            original_action=original_action,
            decision=payload.decision,
            notes=payload.notes,
            reviewer_id=payload.reviewer_id,
            reviewed_at=datetime.utcnow(),
            is_overridden=is_override,
        )
        db.add(new_review)

    # Add audit log record
    audit = AuditLogRecord(
        event_type="HUMAN_REVIEW_DECISION",
        order_id=order_id,
        actor=payload.reviewer_id,
        payload={
            "original_risk_tier": original_tier,
            "original_action": original_action,
            "decision": payload.decision,
            "is_overridden": is_override,
            "notes": payload.notes,
        },
    )
    db.add(audit)
    db.commit()

    return ReviewDecisionResponse(
        order_id=order_id,
        decision=payload.decision,
        status="OVERRIDDEN" if is_override else "CONFIRMED",
        reviewed_at=datetime.utcnow().isoformat(),
        message=f"Review decision '{payload.decision}' successfully recorded for order {order_id}.",
    )
