"""
Tests for Phase 7: Probability Calibration & Reliability Analysis.
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

from src.ml.calibrate import (
    CALIBRATION_CURVES_PATH,
    CALIBRATED_MODEL_PATH,
    CALIBRATION_METRICS_PATH,
    CALIBRATION_REPORT_PATH,
    compute_calibration_errors,
    run_calibration_pipeline,
)
from src.ml.preprocessing import FeaturePreprocessor

VAL_PATH = PROJECT_ROOT / "data" / "splits" / "val.csv"
PREPROCESSOR_PATH = PROJECT_ROOT / "models" / "preprocessor.joblib"


@pytest.fixture(scope="module")
def val_data():
    if not VAL_PATH.exists():
        pytest.skip("Validation split not found. Run: python src/data/split_dataset.py")
    return pd.read_csv(VAL_PATH)


class TestCalibrationMathFunctions:
    """Test suite for mathematical calibration metric calculations."""

    def test_compute_calibration_errors_perfect(self):
        # Create perfectly calibrated mock distribution
        y_true = np.array([0] * 70 + [1] * 30 + [0] * 20 + [1] * 80)
        y_prob = np.array([0.3] * 100 + [0.8] * 100)
        ece, mce, p_true, p_pred, counts = compute_calibration_errors(y_true, y_prob, n_bins=10)

        assert ece < 0.01, f"Expected near-zero ECE for perfectly calibrated input, got {ece}"
        assert mce < 0.05
        assert len(p_true) == 10
        assert len(p_pred) == 10
        assert len(counts) == 10

    def test_compute_calibration_errors_extreme_bias(self):
        # Biased: model predicts 0.95 for everything, but actual return rate is 0.10
        y_true = np.array([1] * 10 + [0] * 90)
        y_prob = np.array([0.95] * 100)
        ece, mce, _, _, _ = compute_calibration_errors(y_true, y_prob, n_bins=10)

        assert ece > 0.70, f"Expected high ECE for biased input, got {ece}"
        assert mce > 0.70


class TestCalibrationPipelineExecution:
    """Test suite verifying calibration pipeline, artifacts, and reliability benchmarks."""

    def test_calibrated_artifacts_exist(self):
        if not CALIBRATED_MODEL_PATH.exists():
            run_calibration_pipeline()

        assert CALIBRATED_MODEL_PATH.exists(), f"Missing calibrated model at {CALIBRATED_MODEL_PATH}"
        assert CALIBRATION_METRICS_PATH.exists(), f"Missing metrics at {CALIBRATION_METRICS_PATH}"
        assert CALIBRATION_REPORT_PATH.exists(), f"Missing report at {CALIBRATION_REPORT_PATH}"
        assert CALIBRATION_CURVES_PATH.exists(), f"Missing plot at {CALIBRATION_CURVES_PATH}"

    def test_calibrated_metrics_benchmarks(self):
        with open(CALIBRATION_METRICS_PATH) as f:
            meta = json.load(f)

        opt_metrics = meta["optimal_metrics"]
        assert opt_metrics["expected_calibration_error"] < 0.05, (
            f"ECE ({opt_metrics['expected_calibration_error']}) exceeds 0.05 benchmark"
        )
        assert opt_metrics["max_calibration_error"] < 0.15, (
            f"MCE ({opt_metrics['max_calibration_error']}) exceeds 0.15 benchmark"
        )
        assert opt_metrics["brier_score"] < 0.22, (
            f"Brier score ({opt_metrics['brier_score']}) exceeds 0.22 benchmark"
        )
        assert opt_metrics["roc_auc"] >= 0.70, (
            f"Calibrated ROC-AUC ({opt_metrics['roc_auc']}) degraded below 0.70"
        )
        assert opt_metrics["pr_auc"] >= 0.40, (
            f"Calibrated PR-AUC ({opt_metrics['pr_auc']}) degraded below 0.40"
        )

    def test_calibrated_model_inference_pipeline(self, val_data):
        assert PREPROCESSOR_PATH.exists()
        assert CALIBRATED_MODEL_PATH.exists()

        preprocessor = FeaturePreprocessor.load(PREPROCESSOR_PATH)
        calibrated_model = joblib.load(CALIBRATED_MODEL_PATH)

        sample = val_data.head(25)
        X_sample = preprocessor.transform(sample)
        probs = calibrated_model.predict_proba(X_sample)[:, 1]

        assert len(probs) == 25
        assert (probs >= 0.0).all() and (probs <= 1.0).all()

    def test_calibration_report_integrity(self):
        content = CALIBRATION_REPORT_PATH.read_text(encoding="utf-8")
        assert "Probability Calibration & Reliability Report" in content
        assert "Multi-Method Calibration Benchmark Leaderboard" in content
        assert "Bin-Level Empirical Reliability Breakdown" in content
        assert "Architectural Readiness for Phase 8" in content
