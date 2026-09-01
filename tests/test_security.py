"""
Tests for Phase 18: Security Review & Defensive Hardening.
"""

import sys
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
    yield


class TestInputValidationAndBoundarySafeguards:
    """Test suite verifying input validation, boundary enforcement, and injection defense."""

    def test_negative_order_value_rejected(self):
        payload = {
            "order_id": "ORD-MALICIOUS-01",
            "order_value": -500.0,  # Negative price attack
            "product_category": "Electronics",
        }
        res = client.post("/api/v1/score", json=payload)
        assert res.status_code == 422, "Negative order_value should be rejected with 422 Unprocessable Entity"

    def test_invalid_discount_range_rejected(self):
        payload = {
            "order_id": "ORD-MALICIOUS-02",
            "order_value": 1500.0,
            "discount_pct": 150.0,  # > 100% discount
        }
        res = client.post("/api/v1/score", json=payload)
        assert res.status_code == 422, "Discount > 100% should be rejected with 422"

    def test_sql_injection_payload_handled_safely(self):
        malicious_id = "ORD-INJECT'; DROP TABLE orders; --"
        payload = {
            "order_id": malicious_id,
            "order_value": 2000.0,
            "product_category": "Clothing",
            "payment_method": "COD",
        }
        res = client.post("/api/v1/score", json=payload)
        assert res.status_code == 200, "SQL injection string should be safely escaped by ORM without breaking"
        data = res.json()
        assert data["order_id"] == malicious_id

        # Verify database still intact
        health_res = client.get("/api/v1/health")
        assert health_res.status_code == 200

    def test_xss_script_tags_handled_safely(self):
        xss_payload = {
            "order_id": "ORD-XSS-<script>alert(1)</script>",
            "customer_id": "CUST-<img src=x onerror=alert('xss')>",
            "order_value": 2500.0,
            "product_category": "Footwear",
        }
        res = client.post("/api/v1/score", json=xss_payload)
        assert res.status_code == 200
        data = res.json()
        assert "ORD-XSS-" in data["order_id"]

    def test_pagination_bounds_enforced(self):
        # Limit > 200 should be rejected by query validation
        res = client.get("/api/v1/orders?limit=9999")
        assert res.status_code == 422, "Excessive pagination limit should be rejected with 422"
