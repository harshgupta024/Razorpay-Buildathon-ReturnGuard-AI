"""
Tests for Phase 19: Comprehensive End-to-End System Integration Suite.

Verifies the complete life-cycle dataflow:
Raw Input -> Preprocessing -> Calibrated ML -> Cost Engine -> Explainability ->
FastAPI REST -> Database Persistence -> Human Review Override -> Audit Logging -> Portfolio Analytics.
"""

import sys
import uuid
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.app import app
from src.db.session import init_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()
    client.post("/api/v1/config/thresholds", json={"preset_name": "Balanced"})
    yield
    client.post("/api/v1/config/thresholds", json={"preset_name": "Balanced"})


class TestEndToEndSystemIntegration:
    """Complete end-to-end multi-step system test."""

    def test_full_order_lifecycle_from_score_to_review_override(self):
        order_id = f"ORD-E2E-{uuid.uuid4().hex[:6].upper()}"

        # Step 1: Submit high-risk order for real-time scoring
        order_payload = {
            "order_id": order_id,
            "customer_id": "CUST-E2E-001",
            "product_id": "PROD-FASH-99",
            "order_value": 12000.0,
            "product_category": "Clothing",
            "payment_method": "COD",
            "quantity": 3,
            "discount_pct": 50.0,
            "customer_return_rate": 0.85,
            "customer_total_orders": 5,
            "customer_total_returns": 4,
            "customer_account_age_days": 10,
            "product_return_rate": 0.45,
            "product_avg_rating": 2.5,
            "order_value_deviation": 4.0,
            "is_first_order": 0,
        }
        score_res = client.post("/api/v1/score", json=order_payload)
        assert score_res.status_code == 200
        score_data = score_res.json()

        assert score_data["order_id"] == order_id
        assert score_data["risk_tier"] in ["HIGH", "CRITICAL"]
        assert score_data["gross_return_loss_inr"] > 1000.0
        assert len(score_data["top_risk_factors"]) > 0
        assert len(score_data["action_evaluations"]) == 5

        # Step 2: Verify order is listed in the orders feed
        orders_res = client.get(f"/api/v1/orders")
        assert orders_res.status_code == 200
        orders_list = orders_res.json()["orders"]
        matched_order = next((o for o in orders_list if o["order_id"] == order_id), None)
        assert matched_order is not None
        assert matched_order["assessment"]["risk_tier"] in ["HIGH", "CRITICAL"]

        # Step 3: Verify order is present in the Human Review Queue
        queue_res = client.get("/api/v1/review/queue?status_filter=PENDING")
        assert queue_res.status_code == 200
        queue_items = queue_res.json()["queue"]
        queue_order = next((q for q in queue_items if q["order_id"] == order_id), None)
        assert queue_order is not None
        assert queue_order["review_status"] == "PENDING"

        # Step 4: Inspect full detail view with explainability
        detail_res = client.get(f"/api/v1/orders/{order_id}")
        assert detail_res.status_code == 200
        detail_data = detail_res.json()
        assert detail_data["assessment"]["plain_language_summary"] is not None
        assert len(detail_data["audit_logs"]) >= 1
        assert detail_data["audit_logs"][0]["event_type"] == "ORDER_SCORED"

        # Step 5: Merchant submits a human review decision override
        decision_payload = {
            "decision": "APPROVED_SEAMLESS",
            "notes": "Spoke to customer via phone call; confirmed size 10 and delivery address.",
            "reviewer_id": "senior_merchant_lead",
        }
        decision_res = client.post(f"/api/v1/review/{order_id}/decision", json=decision_payload)
        assert decision_res.status_code == 200
        decision_data = decision_res.json()
        assert decision_data["status"] == "OVERRIDDEN"

        # Step 6: Verify review status updated in order detail and audit log
        updated_detail_res = client.get(f"/api/v1/orders/{order_id}")
        updated_detail = updated_detail_res.json()
        assert updated_detail["review"] is not None
        assert updated_detail["review"]["decision"] == "APPROVED_SEAMLESS"
        assert updated_detail["review"]["is_overridden"] is True
        assert len(updated_detail["audit_logs"]) >= 2
        assert any(al["event_type"] == "HUMAN_REVIEW_DECISION" for al in updated_detail["audit_logs"])

        # Step 7: Verify portfolio analytics reflect the new scored order
        analytics_res = client.get("/api/v1/analytics/summary")
        assert analytics_res.status_code == 200
        analytics = analytics_res.json()
        assert analytics["total_orders_analyzed"] >= 1
        assert analytics["total_portfolio_value_inr"] >= 7800.0

    def test_e2e_batch_scoring_and_analytics_aggregation(self):
        batch_orders = [
            {"order_id": f"ORD-BATCH-E2E-{i}", "order_value": 1500.0 + (i * 500), "product_category": "Clothing", "payment_method": "UPI"}
            for i in range(10)
        ]
        res = client.post("/api/v1/score/batch", json={"orders": batch_orders})
        assert res.status_code == 200
        data = res.json()

        assert data["total_orders_scored"] == 10
        assert len(data["results"]) == 10
        assert data["total_expected_loss_inr"] > 0

    def test_e2e_strategy_preset_switching(self):
        # 1. Check current preset
        get_res = client.get("/api/v1/config/thresholds")
        assert get_res.status_code == 200

        # 2. Switch to Aggressive
        agg_res = client.post("/api/v1/config/thresholds", json={"preset_name": "Aggressive"})
        assert agg_res.status_code == 200
        assert agg_res.json()["new_cutoffs"]["low"] == 0.15

        # 3. Switch back to Balanced
        bal_res = client.post("/api/v1/config/thresholds", json={"preset_name": "Balanced"})
        assert bal_res.status_code == 200
        assert bal_res.json()["new_cutoffs"]["low"] == 0.20
