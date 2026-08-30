"""
Tests for Phase 6: Advanced Models (XGBoost / LightGBM) & Champion Selection.
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ml.preprocessing import FeaturePreprocessor
from src.ml.train_advanced import (
    CHAMPION_MODEL_PATH,
    COMPARISON_JSON_PATH,
    COMPARISON_REPORT_PATH,
    MODEL_METADATA_PATH,
    benchmark_inference_latency,
    get_candidate_models,
    train_and_evaluate_all_models,
)

TRAIN_PATH = PROJECT_ROOT / "data" / "splits" / "train.csv"
VAL_PATH = PROJECT_ROOT / "data" / "splits" / "val.csv"
PREPROCESSOR_PATH = PROJECT_ROOT / "models" / "preprocessor.joblib"


@pytest.fixture(scope="module")
def val_data():
    if not VAL_PATH.exists():
        pytest.skip("Validation dataset split not found. Run: python src/data/split_dataset.py")
    return pd.read_csv(VAL_PATH)


class TestCandidateModelInstantiation:
    """Test suite verifying model definitions and hyperparameter setup."""

    def test_get_candidate_models_contains_all_architectures(self):
        models = get_candidate_models(scale_pos_weight=2.69)
        expected = ["Logistic Regression (Baseline)", "Random Forest", "HistGradientBoosting", "XGBoost"]
        for name in expected:
            assert name in models, f"Missing candidate architecture: {name}"

    def test_candidate_models_have_random_state(self):
        models = get_candidate_models(scale_pos_weight=2.69)
        for name, model in models.items():
            assert hasattr(model, "random_state"), f"{name} must have random_state for reproducibility"


class TestAdvancedModelTrainingAndChampion:
    """Test suite verifying multi-model comparison, champion selection, and artifact integrity."""

    def test_model_comparison_artifacts_exist(self):
        if not CHAMPION_MODEL_PATH.exists():
            train_and_evaluate_all_models()

        assert CHAMPION_MODEL_PATH.exists(), f"Champion model missing at {CHAMPION_MODEL_PATH}"
        assert MODEL_METADATA_PATH.exists(), f"Metadata missing at {MODEL_METADATA_PATH}"
        assert COMPARISON_JSON_PATH.exists(), f"Comparison JSON missing at {COMPARISON_JSON_PATH}"
        assert COMPARISON_REPORT_PATH.exists(), f"Report missing at {COMPARISON_REPORT_PATH}"

    def test_comparison_json_contains_all_models(self):
        with open(COMPARISON_JSON_PATH) as f:
            comparison = json.load(f)

        expected = ["Logistic Regression (Baseline)", "Random Forest", "HistGradientBoosting", "XGBoost"]
        for name in expected:
            assert name in comparison, f"Model {name} missing in comparison results"
            assert "validation_metrics" in comparison[name]
            assert "inference_latency_ms" in comparison[name]

    def test_champion_outperforms_or_matches_baseline(self):
        with open(COMPARISON_JSON_PATH) as f:
            comparison = json.load(f)

        baseline_roc = comparison["Logistic Regression (Baseline)"]["validation_metrics"]["roc_auc"]
        with open(MODEL_METADATA_PATH) as f:
            meta = json.load(f)

        champ_roc = meta["champion_metrics"]["roc_auc"]
        champ_pr = meta["champion_metrics"]["pr_auc"]

        assert champ_roc >= baseline_roc, f"Champion ROC ({champ_roc}) should outperform/match baseline ({baseline_roc})"
        assert champ_pr >= 0.40, f"Champion PR-AUC ({champ_pr}) should meet minimum benchmark 0.40"

    def test_champion_inference_latency(self):
        with open(MODEL_METADATA_PATH) as f:
            meta = json.load(f)

        latency = meta["inference_latency_ms"]
        assert latency < 10.0, f"Inference latency ({latency:.3f}ms) exceeds real-time checkout limit of 10ms"

    def test_champion_model_prediction_pipeline(self, val_data):
        assert PREPROCESSOR_PATH.exists()
        assert CHAMPION_MODEL_PATH.exists()

        preprocessor = FeaturePreprocessor.load(PREPROCESSOR_PATH)
        champion_model = joblib.load(CHAMPION_MODEL_PATH)

        sample = val_data.head(20)
        X_sample = preprocessor.transform(sample)
        probs = champion_model.predict_proba(X_sample)[:, 1]

        assert len(probs) == 20
        assert (probs >= 0.0).all() and (probs <= 1.0).all()

    def test_comparison_report_content(self):
        content = COMPARISON_REPORT_PATH.read_text(encoding="utf-8")
        assert "Multi-Model Performance Leaderboard" in content
        assert "Champion Model Analysis" in content
        assert "Champion Feature Importance Profile" in content
        assert "Transition to Phase 7: Probability Calibration" in content
