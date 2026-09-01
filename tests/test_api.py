"""
Tests for Phase 12 & Phase 15: FastAPI REST API & Human Review Endpoints.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.app import app
from src.db.session import Base, engine, init_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()
    yield


class TestHealthAndSystemEndpoints:
    """Test suite for system health and metadata routes."""

    def test_root_endpoint(self):
        res = client.get("/")
        assert res.status_code == 200
        data = res.json()
        assert "ReturnGuard AI" in data["app"]
        assert data["status"] == "operational"

    def test_health_check_endpoint(self):
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["model_calibrated"] is True


class TestScoringEndpoints:
    """Test suite for real-time and batch order scoring."""

    def test_score_single_order(self):
        payload = {
            "order_id": "ORD-API-TEST-01",
            "customer_id": "CUST-9999",
            "product_id": "PROD-8888",
            "order_value": 4500.0,
            "product_category": "Clothing",
            "payment_method": "COD",
            "quantity": 2,
            "discount_pct": 25.0,
            "customer_return_rate": 0.40,
            "customer_account_age_days": 45,
            "product_return_rate": 0.32,
            "order_value_deviation": 2.1,
        }
        res = client.post("/api/v1/score", json=payload)
        assert res.status_code == 200
        data = res.json()

        assert data["order_id"] == "ORD-API-TEST-01"
        assert 0.0 <= data["predicted_return_probability"] <= 1.0
        assert data["risk_tier"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert data["gross_return_loss_inr"] > 0
        assert "recommended_action" in data
        assert len(data["top_risk_factors"]) > 0
        assert len(data["action_evaluations"]) == 5

    def test_score_batch_orders(self):
        payload = {
            "orders": [
                {"order_id": "ORD-BATCH-01", "order_value": 1500.0, "product_category": "Books", "payment_method": "UPI"},
                {"order_id": "ORD-BATCH-02", "order_value": 8500.0, "product_category": "Clothing", "payment_method": "COD"},
            ]
        }
        res = client.post("/api/v1/score/batch", json=payload)
        assert res.status_code == 200
        data = res.json()

        assert data["total_orders_scored"] == 2
        assert len(data["results"]) == 2
        assert data["total_expected_loss_inr"] >= 0


class TestOrdersAndHistoricalFeed:
    """Test suite for orders querying and detail inspection."""

    def test_list_orders_feed(self):
        res = client.get("/api/v1/orders?limit=10")
        assert res.status_code == 200
        data = res.json()

        assert "total_count" in data
        assert isinstance(data["orders"], list)
        assert data["limit"] == 10

    def test_get_order_detail_existing(self):
        res = client.get("/api/v1/orders/ORD-API-TEST-01")
        assert res.status_code == 200
        data = res.json()

        assert data["order_id"] == "ORD-API-TEST-01"
        assert data["assessment"] is not None
        assert "plain_language_summary" in data["assessment"]
        assert "top_risk_factors" in data["assessment"]

    def test_get_order_detail_not_found(self):
        res = client.get("/api/v1/orders/ORD-NONEXISTENT-999")
        assert res.status_code == 404


class TestHumanInTheLoopReviewQueue:
    """Test suite for Phase 15 human review queue & merchant overrides."""

    def test_review_queue_retrieval(self):
        res = client.get("/api/v1/review/queue?status_filter=ALL")
        assert res.status_code == 200
        data = res.json()
        assert "total_queue_count" in data
        assert "queue" in data

    def test_submit_review_decision(self):
        decision_payload = {
            "decision": "APPROVED_SEAMLESS",
            "notes": "Verified VIP customer manually via WhatsApp.",
            "reviewer_id": "merchant_lead",
        }
        res = client.post("/api/v1/review/ORD-API-TEST-01/decision", json=decision_payload)
        assert res.status_code == 200
        data = res.json()

        assert data["order_id"] == "ORD-API-TEST-01"
        assert data["decision"] == "APPROVED_SEAMLESS"
        assert "successfully recorded" in data["message"]

        # Verify detail view includes review
        detail_res = client.get("/api/v1/orders/ORD-API-TEST-01")
        detail_data = detail_res.json()
        assert detail_data["review"] is not None
        assert detail_data["review"]["decision"] == "APPROVED_SEAMLESS"


class TestAnalyticsAndConfigEndpoints:
    """Test suite for portfolio analytics and threshold presets."""

    def test_analytics_summary(self):
        res = client.get("/api/v1/analytics/summary")
        assert res.status_code == 200
        data = res.json()

        assert data["total_orders_analyzed"] >= 1
        assert "tier_distribution" in data
        assert "category_breakdown" in data

    def test_get_and_update_threshold_presets(self):
        get_res = client.get("/api/v1/config/thresholds")
        assert get_res.status_code == 200
        get_data = get_res.json()
        assert "active_preset" in get_data
        assert "available_presets" in get_data

        # Update to Conservative
        update_res = client.post("/api/v1/config/thresholds", json={"preset_name": "Conservative"})
        assert update_res.status_code == 200
        update_data = update_res.json()
        assert "Conservative" in update_data["active_preset"]
        assert update_data["new_cutoffs"]["low"] == 0.30

        # Reset back to Balanced
        reset_res = client.post("/api/v1/config/thresholds", json={"preset_name": "Balanced"})
        assert reset_res.status_code == 200
