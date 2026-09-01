"""
Tests for Phase 9: Business Cost & Financial Simulation Engine.
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.business.cost_engine import (
    BusinessCostEngine,
    MitigationActionType,
    OrderFinancialProfile,
    CATEGORY_DEPRECIATION_RATES,
)


class TestOrderFinancialProfile:
    """Test suite for financial loss breakdown calculations."""

    def test_gross_return_loss_calculation(self):
        profile = OrderFinancialProfile(
            order_value=5000.0,
            product_category="Clothing",
            product_weight_grams=1000.0,
        )
        # Expected: forward (100) + return (150) + restocking (80) + packaging (40) + depreciation (5000 * 0.18 = 900) = 1270
        assert profile.product_depreciation_loss == 900.0
        assert profile.gross_return_loss == 1270.0

    def test_weight_surcharge_application(self):
        # Weight 4500g = 2.5kg extra -> 2.5 * 40 = 100 extra return shipping
        profile = OrderFinancialProfile(
            order_value=2000.0,
            product_category="Electronics",
            product_weight_grams=4500.0,
        )
        assert profile.return_shipping_cost == 250.0  # 150 base + 100 surcharge

    def test_category_depreciation_coverage(self):
        categories = ["Electronics", "Clothing", "Footwear", "Beauty", "Home", "Books", "Sports", "Accessories"]
        for cat in categories:
            assert cat in CATEGORY_DEPRECIATION_RATES
            profile = OrderFinancialProfile(order_value=1000.0, product_category=cat)
            assert profile.depreciation_rate == CATEGORY_DEPRECIATION_RATES[cat]


class TestBusinessCostEngine:
    """Test suite for mitigation policy simulations and profit-maximizing recommendations."""

    def test_low_risk_order_recommends_seamless(self):
        engine = BusinessCostEngine()
        profile = OrderFinancialProfile(order_value=1500.0, product_category="Books")
        assessment = engine.evaluate_order(profile, return_probability=0.04)

        assert assessment.recommended_action == MitigationActionType.ALLOW_SEAMLESS
        assert assessment.unmitigated_expected_loss < 50.0
        assert "Seamless 1-click fulfillment" in assessment.action_rationale

    def test_high_risk_order_recommends_mitigation(self):
        engine = BusinessCostEngine()
        profile = OrderFinancialProfile(order_value=8000.0, product_category="Clothing", payment_method="COD")
        assessment = engine.evaluate_order(profile, return_probability=0.65)

        assert assessment.recommended_action in [
            MitigationActionType.WHATSAPP_CONFIRMATION,
            MitigationActionType.REQUIRE_PREPAID_OR_DEPOSIT,
            MitigationActionType.MANUAL_REVIEW_CALL,
        ]
        assert assessment.expected_net_savings > 200.0
        assert assessment.mitigated_expected_loss < assessment.unmitigated_expected_loss

    def test_action_evaluations_completeness(self):
        engine = BusinessCostEngine()
        profile = OrderFinancialProfile(order_value=3000.0, product_category="Electronics")
        assessment = engine.evaluate_order(profile, return_probability=0.35)

        assert len(assessment.action_evaluations) == 5
        recommended_count = sum(1 for e in assessment.action_evaluations if e.is_recommended)
        assert recommended_count == 1

    def test_to_dict_serialization(self):
        engine = BusinessCostEngine()
        profile = OrderFinancialProfile(order_value=2500.0, product_category="Footwear")
        assessment = engine.evaluate_order(profile, return_probability=0.25)

        data = assessment.to_dict()
        assert "gross_return_loss" in data
        assert "unmitigated_expected_loss" in data
        assert "recommended_action" in data
        assert "expected_net_savings" in data
        assert "action_evaluations" in data
        assert isinstance(data["action_evaluations"], list)
