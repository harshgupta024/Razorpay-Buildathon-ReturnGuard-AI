"""
ReturnGuard AI — Scoring Endpoints (/api/v1/score)
"""

import uuid
from dataclasses import asdict
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.backend.schemas import BatchOrderInput, BatchScoreResponse, OrderInput, OrderScoreResponse
from src.db.session import AuditLogRecord, OrderRecord, RiskAssessmentRecord, get_db
from src.explainability.explainer import RiskExplainer
from src.risk.scoring_engine import OrderScoreResult, RiskScoringEngine

router = APIRouter(prefix="/api/v1/score", tags=["Scoring & Decisions"])

# Lazy-loaded singletons for performance
_scoring_engine: RiskScoringEngine | None = None
_explainer: RiskExplainer | None = None


def get_scoring_engine() -> RiskScoringEngine:
    global _scoring_engine
    if _scoring_engine is None:
        _scoring_engine = RiskScoringEngine()
    return _scoring_engine


def get_explainer() -> RiskExplainer:
    global _explainer
    if _explainer is None:
        _explainer = RiskExplainer()
    return _explainer


@router.post("", response_model=OrderScoreResponse, status_code=status.HTTP_200_OK)
def score_single_order(
    payload: OrderInput,
    db: Session = Depends(get_db),
    engine: RiskScoringEngine = Depends(get_scoring_engine),
    explainer: RiskExplainer = Depends(get_explainer),
):
    """
    Score a single order in real time:
    - Preprocesses inputs & predicts calibrated return risk probability
    - Assigns risk tier (LOW, MEDIUM, HIGH, CRITICAL)
    - Simulates financial loss & recommends profit-maximizing mitigation policy
    - Generates ethical, non-accusatory SHAP feature attributions
    - Persists order and assessment to database with audit logging
    """
    order_dict = payload.model_dump()
    if not order_dict.get("order_id"):
        order_dict["order_id"] = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    # 1. Run Risk Scoring Engine
    score_res: OrderScoreResult = engine.score_order(order_dict)

    # 2. Run Explainability Engine
    explanation = explainer.explain_order(order_dict)

    # 3. Persist to Database (Upsert order and assessment)
    existing_order = db.query(OrderRecord).filter_by(order_id=score_res.order_id).first()
    if existing_order:
        # Update existing order fields
        for k, v in order_dict.items():
            if hasattr(existing_order, k) and k != "order_id":
                setattr(existing_order, k, v)
        order_rec = existing_order
    else:
        order_rec = OrderRecord(
            order_id=score_res.order_id,
            customer_id=score_res.customer_id,
            product_id=score_res.product_id,
            order_value=score_res.order_value,
            product_category=score_res.product_category,
            payment_method=score_res.payment_method,
            quantity=order_dict.get("quantity", 1),
            discount_pct=order_dict.get("discount_pct", 0.0),
            customer_account_age_days=order_dict.get("customer_account_age_days", 30),
            customer_total_orders=order_dict.get("customer_total_orders", 1),
            customer_total_returns=order_dict.get("customer_total_returns", 0),
            customer_return_rate=order_dict.get("customer_return_rate", 0.0),
            product_price=order_dict.get("product_price", score_res.order_value),
            product_weight_grams=order_dict.get("product_weight_grams", 1000.0),
            product_return_rate=order_dict.get("product_return_rate", 0.20),
            order_value_deviation=order_dict.get("order_value_deviation", 1.0),
            is_first_order=order_dict.get("is_first_order", 0),
        )
        db.add(order_rec)

    # Update or add assessment
    existing_assessment = db.query(RiskAssessmentRecord).filter_by(order_id=score_res.order_id).first()
    if existing_assessment:
        existing_assessment.predicted_return_probability = score_res.predicted_return_probability
        existing_assessment.risk_score = score_res.risk_score
        existing_assessment.risk_tier = score_res.risk_tier.value
        existing_assessment.gross_return_loss_inr = score_res.gross_return_loss_inr
        existing_assessment.unmitigated_expected_loss_inr = score_res.unmitigated_expected_loss_inr
        existing_assessment.recommended_action = score_res.recommended_action.value
        existing_assessment.recommended_action_name = score_res.recommended_action_name
        existing_assessment.expected_net_savings_inr = score_res.expected_net_savings_inr
        existing_assessment.mitigated_expected_loss_inr = score_res.mitigated_expected_loss_inr
        existing_assessment.action_rationale = score_res.action_rationale
        existing_assessment.top_risk_factors = [asdict(rf) for rf in explanation.top_risk_factors]
        existing_assessment.top_protective_factors = [asdict(rf) for rf in explanation.top_protective_factors]
        existing_assessment.plain_language_summary = explanation.plain_language_summary
        existing_assessment.latency_ms = score_res.latency_ms
    else:
        assessment_rec = RiskAssessmentRecord(
            order_id=score_res.order_id,
            predicted_return_probability=score_res.predicted_return_probability,
            risk_score=score_res.risk_score,
            risk_tier=score_res.risk_tier.value,
            gross_return_loss_inr=score_res.gross_return_loss_inr,
            unmitigated_expected_loss_inr=score_res.unmitigated_expected_loss_inr,
            recommended_action=score_res.recommended_action.value,
            recommended_action_name=score_res.recommended_action_name,
            expected_net_savings_inr=score_res.expected_net_savings_inr,
            mitigated_expected_loss_inr=score_res.mitigated_expected_loss_inr,
            action_rationale=score_res.action_rationale,
            top_risk_factors=[asdict(rf) for rf in explanation.top_risk_factors],
            top_protective_factors=[asdict(rf) for rf in explanation.top_protective_factors],
            plain_language_summary=explanation.plain_language_summary,
            latency_ms=score_res.latency_ms,
        )
        db.add(assessment_rec)

    # Audit Log
    audit = AuditLogRecord(
        event_type="ORDER_SCORED",
        order_id=score_res.order_id,
        actor="system",
        payload={
            "risk_tier": score_res.risk_tier.value,
            "risk_score": score_res.risk_score,
            "recommended_action": score_res.recommended_action.value,
            "expected_net_savings_inr": score_res.expected_net_savings_inr,
        },
    )
    db.add(audit)
    db.commit()

    return OrderScoreResponse(
        order_id=score_res.order_id,
        customer_id=score_res.customer_id,
        product_id=score_res.product_id,
        order_value=score_res.order_value,
        product_category=score_res.product_category,
        payment_method=score_res.payment_method,
        predicted_return_probability=score_res.predicted_return_probability,
        risk_score=score_res.risk_score,
        risk_tier=score_res.risk_tier.value,
        gross_return_loss_inr=score_res.gross_return_loss_inr,
        unmitigated_expected_loss_inr=score_res.unmitigated_expected_loss_inr,
        recommended_action=score_res.recommended_action.value,
        recommended_action_name=score_res.recommended_action_name,
        expected_net_savings_inr=score_res.expected_net_savings_inr,
        mitigated_expected_loss_inr=score_res.mitigated_expected_loss_inr,
        action_rationale=score_res.action_rationale,
        action_evaluations=score_res.action_evaluations,
        top_risk_factors=[asdict(rf) for rf in explanation.top_risk_factors],
        top_protective_factors=[asdict(rf) for rf in explanation.top_protective_factors],
        plain_language_summary=explanation.plain_language_summary,
        scored_at=score_res.scored_at,
        latency_ms=score_res.latency_ms,
    )


@router.post("/batch", response_model=BatchScoreResponse, status_code=status.HTTP_200_OK)
def score_order_batch(
    payload: BatchOrderInput,
    db: Session = Depends(get_db),
    engine: RiskScoringEngine = Depends(get_scoring_engine),
    explainer: RiskExplainer = Depends(get_explainer),
):
    """Batch scoring for high-volume order ingestion."""
    results: List[OrderScoreResponse] = []
    total_loss = 0.0
    total_savings = 0.0

    for item in payload.orders:
        single_res = score_single_order(item, db=db, engine=engine, explainer=explainer)
        results.append(single_res)
        total_loss += single_res.unmitigated_expected_loss_inr
        total_savings += single_res.expected_net_savings_inr

    return BatchScoreResponse(
        total_orders_scored=len(results),
        total_expected_loss_inr=round(total_loss, 2),
        total_expected_net_savings_inr=round(total_savings, 2),
        results=results,
    )
