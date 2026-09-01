"""
Tests for Phase 10: Unified Production Risk Scoring Engine.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.risk.scoring_engine import OrderScoreResult, RiskScoringEngine
from src.risk.thresholds import RiskTier

VAL_PATH = PROJECT_ROOT / "data" / "splits" / "val.csv"


@pytest.fixture(scope="module")
def val_data():
    if not VAL_PATH.exists():
        pytest.skip("Validation dataset split not found.")
    return pd.read_csv(VAL_PATH)


@pytest.fixture(scope="module")
def scoring_engine():
    return RiskScoringEngine()


class TestRiskScoringEngine:
    """Test suite for real-time and batch risk scoring operations."""

    def test_engine_initialization(self, scoring_engine):
        assert scoring_engine.preprocessor is not None
        assert scoring_engine.model is not None
        assert scoring_engine.tier_config is not None
        assert scoring_engine.cost_engine is not None

    def test_score_single_order_dict(self, scoring_engine, val_data):
        # Warmup call
        _ = scoring_engine.score_order(val_data.iloc[0].to_dict())

        order_dict = val_data.iloc[1].to_dict()
        result: OrderScoreResult = scoring_engine.score_order(order_dict)

        assert isinstance(result, OrderScoreResult)
        assert result.order_id == str(order_dict["order_id"])
        assert 0.0 <= result.predicted_return_probability <= 1.0
        assert 0.0 <= result.risk_score <= 100.0
        assert isinstance(result.risk_tier, RiskTier)
        assert result.gross_return_loss_inr > 0
        assert result.unmitigated_expected_loss_inr >= 0
        assert result.expected_net_savings_inr >= 0
        assert result.latency_ms > 0.0
        assert result.latency_ms < 1000.0  # Test execution upper bound on shared CI/CD environments

    def test_score_single_order_series(self, scoring_engine, val_data):
        series = val_data.iloc[5]
        result = scoring_engine.score_order(series)
        assert result.order_id == str(series["order_id"])
        assert result.risk_tier_name in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def test_score_result_serialization(self, scoring_engine, val_data):
        order_dict = val_data.iloc[2].to_dict()
        result = scoring_engine.score_order(order_dict)
        data = result.to_dict()

        assert isinstance(data, dict)
        assert data["order_id"] == result.order_id
        assert data["risk_tier"] == result.risk_tier.value
        assert data["recommended_action"] == result.recommended_action.value
        assert "action_evaluations" in data

    def test_batch_scoring_performance(self, scoring_engine, val_data):
        batch = val_data.head(200).copy()
        scored_batch = scoring_engine.score_batch(batch)

        assert len(scored_batch) == 200
        assert "predicted_return_probability" in scored_batch.columns
        assert "risk_score" in scored_batch.columns
        assert "risk_tier" in scored_batch.columns
        assert "recommended_action" in scored_batch.columns
        assert "expected_net_savings_inr" in scored_batch.columns
        assert (scored_batch["predicted_return_probability"] >= 0.0).all()
        assert (scored_batch["predicted_return_probability"] <= 1.0).all()
