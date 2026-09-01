"""
Tests for Phase 13: Database Layer & Relational Schema.
"""

import sys
from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.db.session import (
    AuditLogRecord,
    Base,
    OrderRecord,
    ReviewRecord,
    RiskAssessmentRecord,
    init_db,
)


@pytest.fixture(scope="module")
def test_db_session():
    """In-memory SQLite session for isolated database testing."""
    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()


class TestDatabaseModels:
    """Test suite verifying database models, constraints, and relationships."""

    def test_init_db_runs_safely(self):
        init_db()  # Verifies file database creation

    def test_order_and_assessment_crud(self, test_db_session):
        order = OrderRecord(
            order_id="ORD-TEST-001",
            customer_id="CUST-100",
            product_id="PROD-200",
            order_value=3500.0,
            product_category="Footwear",
            payment_method="COD",
        )
        test_db_session.add(order)
        test_db_session.commit()

        assessment = RiskAssessmentRecord(
            order_id="ORD-TEST-001",
            predicted_return_probability=0.52,
            risk_score=52.0,
            risk_tier="HIGH",
            gross_return_loss_inr=1100.0,
            unmitigated_expected_loss_inr=572.0,
            recommended_action="WHATSAPP_CONFIRMATION",
            recommended_action_name="WhatsApp Confirmation",
            expected_net_savings_inr=180.0,
            mitigated_expected_loss_inr=392.0,
            action_rationale="High return propensity on COD footwear.",
            top_risk_factors=[{"feature": "payment_method", "reason": "COD"}],
            top_protective_factors=[],
            plain_language_summary="High risk COD footwear order.",
            latency_ms=2.5,
        )
        test_db_session.add(assessment)
        test_db_session.commit()

        # Query back
        fetched_order = test_db_session.query(OrderRecord).filter_by(order_id="ORD-TEST-001").first()
        assert fetched_order is not None
        assert fetched_order.assessment is not None
        assert fetched_order.assessment.risk_tier == "HIGH"
        assert fetched_order.assessment.predicted_return_probability == 0.52

    def test_review_and_audit_log_crud(self, test_db_session):
        review = ReviewRecord(
            order_id="ORD-TEST-001",
            original_risk_tier="HIGH",
            original_action="WHATSAPP_CONFIRMATION",
            decision="APPROVED_WITH_DEPOSIT",
            notes="Customer confirmed size on phone, collected Rs. 100 deposit.",
            reviewer_id="agent_john",
            is_overridden=True,
        )
        test_db_session.add(review)

        audit = AuditLogRecord(
            event_type="REVIEW_OVERRIDDEN",
            order_id="ORD-TEST-001",
            actor="agent_john",
            payload={"decision": "APPROVED_WITH_DEPOSIT", "deposit_inr": 100},
        )
        test_db_session.add(audit)
        test_db_session.commit()

        fetched_order = test_db_session.query(OrderRecord).filter_by(order_id="ORD-TEST-001").first()
        assert fetched_order.review is not None
        assert fetched_order.review.decision == "APPROVED_WITH_DEPOSIT"
        assert fetched_order.review.is_overridden is True
        assert len(fetched_order.audit_logs) == 1
        assert fetched_order.audit_logs[0].event_type == "REVIEW_OVERRIDDEN"
