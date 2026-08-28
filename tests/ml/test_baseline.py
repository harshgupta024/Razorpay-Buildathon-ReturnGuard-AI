"""
Tests for Phase 5: Baseline Model (Logistic Regression) & Preprocessing Pipeline.
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

from src.ml.evaluate import evaluate_predictions, ModelEvaluationResult
from src.ml.preprocessing import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    FeaturePreprocessor,
    prepare_data_splits,
)
from src.ml.train_baseline import (
    MODEL_PATH,
    PREPROCESSOR_PATH,
    REPORT_PATH,
    METRICS_JSON_PATH,
    train_baseline_model,
)

TRAIN_PATH = PROJECT_ROOT / "data" / "splits" / "train.csv"
VAL_PATH = PROJECT_ROOT / "data" / "splits" / "val.csv"


@pytest.fixture(scope="module")
def data_splits():
    if not TRAIN_PATH.exists() or not VAL_PATH.exists():
        pytest.skip("Dataset splits not found. Run: python src/data/split_dataset.py")
    train_df = pd.read_csv(TRAIN_PATH)
    val_df = pd.read_csv(VAL_PATH)
    return train_df, val_df


class TestFeaturePreprocessor:
    """Test suite for data preprocessing and encoding pipeline."""

    def test_fit_transform_shape(self, data_splits):
        train_df, _ = data_splits
        preprocessor = FeaturePreprocessor()
        X_train = preprocessor.fit_transform(train_df)
        assert X_train.shape[0] == len(train_df)
        assert X_train.shape[1] == 36  # 18 numerical + 18 one-hot categoricals
        assert preprocessor.is_fitted

    def test_feature_names_integrity(self, data_splits):
        train_df, _ = data_splits
        preprocessor = FeaturePreprocessor()
        preprocessor.fit(train_df)
        names = preprocessor.get_feature_names()
        assert len(names) == 36
        for num_feat in NUMERICAL_FEATURES:
            assert num_feat in names
        for cat_feat in CATEGORICAL_FEATURES:
            assert any(n.startswith(f"{cat_feat}_") for n in names)

    def test_transform_unseen_categories_safe(self, data_splits):
        train_df, _ = data_splits
        preprocessor = FeaturePreprocessor()
        preprocessor.fit(train_df)

        # Create synthetic order with unseen categories
        sample = train_df.iloc[:2].copy()
        sample["product_category"] = "UnseenCategoryXYZ"
        sample["payment_method"] = "AlienPay"

        transformed = preprocessor.transform(sample)
        assert transformed.shape == (2, 36)
        assert not np.isnan(transformed).any()

    def test_preprocessor_save_and_load(self, data_splits, tmp_path):
        train_df, val_df = data_splits
        preprocessor = FeaturePreprocessor()
        X_val_1 = preprocessor.fit_transform(train_df)

        save_file = tmp_path / "test_preprocessor.joblib"
        preprocessor.save(save_file)

        loaded = FeaturePreprocessor.load(save_file)
        X_val_2 = loaded.transform(train_df)

        np.testing.assert_allclose(X_val_1, X_val_2)


class TestModelEvaluation:
    """Test suite for evaluation metric calculations."""

    def test_evaluate_predictions_perfect(self):
        y_true = np.array([0, 0, 1, 1])
        y_prob = np.array([0.1, 0.2, 0.8, 0.9])
        res = evaluate_predictions(y_true, y_prob, model_name="TestPerfect")
        assert res.roc_auc == 1.0
        assert res.accuracy == 1.0
        assert res.f1 == 1.0
        assert res.brier_score < 0.05

    def test_evaluate_predictions_random(self):
        y_true = np.array([0, 1, 0, 1])
        y_prob = np.array([0.5, 0.5, 0.5, 0.5])
        res = evaluate_predictions(y_true, y_prob, model_name="TestRandom")
        assert 0.0 <= res.roc_auc <= 1.0
        assert 0.0 <= res.pr_auc <= 1.0
        assert isinstance(res.summary_table(), str)


class TestBaselineModelTraining:
    """Test suite for end-to-end baseline model execution & artifact verification."""

    def test_baseline_artifacts_exist(self):
        if not MODEL_PATH.exists():
            train_baseline_model()
        assert MODEL_PATH.exists()
        assert PREPROCESSOR_PATH.exists()
        assert REPORT_PATH.exists()
        assert METRICS_JSON_PATH.exists()

    def test_baseline_performance_benchmarks(self):
        with open(METRICS_JSON_PATH) as f:
            metrics = json.load(f)

        val_metrics = metrics["validation_metrics"]
        assert val_metrics["roc_auc"] >= 0.65, f"Validation ROC-AUC too low: {val_metrics['roc_auc']}"
        assert val_metrics["pr_auc"] >= 0.35, f"Validation PR-AUC too low: {val_metrics['pr_auc']}"
        assert val_metrics["f1"] >= 0.45, f"Validation F1 too low: {val_metrics['f1']}"
        assert val_metrics["brier_score"] <= 0.25, f"Validation Brier too high: {val_metrics['brier_score']}"

    def test_loaded_model_inference(self, data_splits):
        _, val_df = data_splits
        preprocessor = FeaturePreprocessor.load(PREPROCESSOR_PATH)
        model = joblib.load(MODEL_PATH)

        X_sample = preprocessor.transform(val_df.head(10))
        probs = model.predict_proba(X_sample)[:, 1]

        assert len(probs) == 10
        assert (probs >= 0.0).all() and (probs <= 1.0).all()
