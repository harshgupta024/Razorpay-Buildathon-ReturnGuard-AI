"""
Tests for Phase 11: Explainability Engine & Non-Accusatory Explanations.
"""

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.explainability.explainer import (
    OrderExplanation,
    RiskExplainer,
    RiskFactor,
    format_non_accusatory_reason,
)

VAL_PATH = PROJECT_ROOT / "data" / "splits" / "val.csv"

FORBIDDEN_WORDS = [
    "fraud",
    "fraudster",
    "abuser",
    "scammer",
    "cheat",
    "dishonest",
    "guilty",
    "criminal",
    "suspicious person",
]


@pytest.fixture(scope="module")
def val_data():
    if not VAL_PATH.exists():
        pytest.skip("Validation split not found.")
    return pd.read_csv(VAL_PATH)


@pytest.fixture(scope="module")
def explainer():
    return RiskExplainer()


class TestNonAccusatoryEthicalGuardrails:
    """Test suite ensuring all generated explanations adhere strictly to responsible AI principles."""

    def test_reason_formatter_forbidden_words(self):
        test_features = [
            ("customer_return_rate", 0.45, 0.25),
            ("customer_return_rate", 0.05, -0.15),
            ("order_value_deviation", 3.2, 0.40),
            ("payment_method_COD", "COD", 0.30),
            ("discount_pct", 40.0, 0.15),
            ("product_avg_rating", 2.8, 0.20),
            ("is_first_order", 1, 0.10),
            ("customer_account_age_days", 5, 0.10),
        ]

        for feat, val, attr in test_features:
            reason = format_non_accusatory_reason(feat, val, attr)
            for word in FORBIDDEN_WORDS:
                assert word not in reason.lower(), f"Forbidden word '{word}' found in reason: '{reason}'"

    def test_explanation_summary_forbidden_words(self, explainer, val_data):
        # Test 50 diverse orders across the validation set
        sample = val_data.head(50)
        for _, row in sample.iterrows():
            explanation = explainer.explain_order(row)
            summary = explanation.plain_language_summary.lower()

            for word in FORBIDDEN_WORDS:
                assert word not in summary, f"Forbidden word '{word}' found in summary: '{summary}'"

            for rf in explanation.top_risk_factors:
                rf_text = rf.human_readable_reason.lower()
                for word in FORBIDDEN_WORDS:
                    assert word not in rf_text, f"Forbidden word '{word}' found in risk factor: '{rf_text}'"


class TestRiskExplainerPipeline:
    """Test suite for end-to-end explainability calculations and data structures."""

    def test_explain_single_order(self, explainer, val_data):
        row = val_data.iloc[0]
        explanation = explainer.explain_order(row)

        assert isinstance(explanation, OrderExplanation)
        assert explanation.order_id == str(row["order_id"])
        assert 0.0 <= explanation.predicted_return_probability <= 1.0
        assert explanation.risk_tier in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert len(explanation.top_risk_factors) > 0
        assert len(explanation.plain_language_summary) > 10

    def test_risk_factor_data_structure(self, explainer, val_data):
        row = val_data.iloc[10]
        explanation = explainer.explain_order(row)

        for rf in explanation.top_risk_factors:
            assert isinstance(rf, RiskFactor)
            assert rf.attribution_score > 0
            assert rf.direction == "ELEVATES_RISK"
            assert rf.importance_rank >= 1

        for pf in explanation.top_protective_factors:
            assert isinstance(pf, RiskFactor)
            assert pf.attribution_score < 0
            assert pf.direction == "REDUCES_RISK"

    def test_to_dict_serialization(self, explainer, val_data):
        row = val_data.iloc[3]
        explanation = explainer.explain_order(row)
        data = explanation.to_dict()

        assert isinstance(data, dict)
        assert "order_id" in data
        assert "predicted_return_probability" in data
        assert "top_risk_factors" in data
        assert "top_protective_factors" in data
        assert "plain_language_summary" in data

        # Check JSON serializability
        json_str = json.dumps(data)
        assert len(json_str) > 50
