"""
ReturnGuard AI — Preprocessing and Feature Pipeline

Handles data transformation for model training and production inference:
1. Column-specific transformations (Numerical scaling, Categorical One-Hot Encoding)
2. Safe out-of-vocabulary handling for unseen categorical levels
3. Artifact persistence (saving/loading preprocessor pipeline)
4. Fit strictly on train split to prevent data leakage

Usage:
    from src.ml.preprocessing import FeaturePreprocessor
"""

import logging
import sys
from pathlib import Path
from typing import Any, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import MLConfig

logger = logging.getLogger(__name__)

# Feature Definition Schema
CATEGORICAL_FEATURES = [
    "product_category",
    "payment_method",
    "customer_segment",
]

NUMERICAL_FEATURES = [
    "order_value",
    "quantity",
    "discount_pct",
    "is_first_order",
    "customer_account_age_days",
    "customer_total_orders",
    "customer_total_returns",
    "customer_return_rate",
    "customer_avg_order_value",
    "customer_days_since_last_order",
    "product_price",
    "product_weight_grams",
    "product_return_rate",
    "product_avg_rating",
    "order_value_deviation",
    "order_hour",
    "order_day_of_week",
    "is_weekend_order",
]

METADATA_COLUMNS = [
    "order_id",
    "customer_id",
    "product_id",
    "order_date",
]

TARGET_COL = "is_returned"


class FeaturePreprocessor:
    """Preprocesses raw order data into standardized ML features."""

    def __init__(self):
        self.numerical_features = NUMERICAL_FEATURES
        self.categorical_features = CATEGORICAL_FEATURES
        self.target_col = TARGET_COL
        self.pipeline: ColumnTransformer | None = None
        self.feature_names: list[str] | None = None
        self.is_fitted: bool = False

    def _build_pipeline(self) -> ColumnTransformer:
        """Construct the sklearn ColumnTransformer pipeline."""
        num_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )

        cat_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
                (
                    "onehot",
                    OneHotEncoder(
                        handle_unknown="ignore",
                        sparse_output=False,
                    ),
                ),
            ]
        )

        transformer = ColumnTransformer(
            transformers=[
                ("num", num_pipeline, self.numerical_features),
                ("cat", cat_pipeline, self.categorical_features),
            ],
            remainder="drop",
        )
        return transformer

    def fit(self, df: pd.DataFrame) -> "FeaturePreprocessor":
        """Fit preprocessing pipeline strictly on training data."""
        logger.info("Fitting feature preprocessor...")
        self.pipeline = self._build_pipeline()
        self.pipeline.fit(df)

        # Extract generated feature names
        num_names = self.numerical_features
        cat_encoder = self.pipeline.named_transformers_["cat"].named_steps["onehot"]
        cat_names = list(cat_encoder.get_feature_names_out(self.categorical_features))
        self.feature_names = num_names + cat_names

        self.is_fitted = True
        logger.info("Preprocessor fitted successfully. Total feature dimensionality: %d", len(self.feature_names))
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transform dataset using fitted pipeline."""
        if not self.is_fitted or self.pipeline is None:
            raise RuntimeError("FeaturePreprocessor is not fitted. Call fit() or load() first.")
        return self.pipeline.transform(df)

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        """Fit on training data and transform."""
        self.fit(df)
        return self.transform(df)

    def transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform and return DataFrame with named columns."""
        arr = self.transform(df)
        return pd.DataFrame(arr, columns=self.feature_names, index=df.index)

    def get_feature_names(self) -> list[str]:
        """Return list of transformed feature names."""
        if self.feature_names is None:
            raise RuntimeError("Preprocessor is not fitted.")
        return self.feature_names

    def save(self, filepath: Path | str) -> None:
        """Serialize preprocessor to disk."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, filepath)
        logger.info("Saved preprocessor artifact to %s", filepath)

    @classmethod
    def load(cls, filepath: Path | str) -> "FeaturePreprocessor":
        """Load serialized preprocessor from disk."""
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Preprocessor artifact not found at {filepath}")
        obj = joblib.load(filepath)
        if not isinstance(obj, FeaturePreprocessor):
            raise TypeError(f"Expected FeaturePreprocessor object, got {type(obj)}")
        logger.info("Loaded preprocessor artifact from %s", filepath)
        return obj


def prepare_data_splits(
    train_path: Path | str,
    val_path: Path | str,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, FeaturePreprocessor]:
    """Helper to load train and val datasets, fit preprocessor on train, and return (X_train, y_train, X_val, y_val, preprocessor)."""
    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)

    preprocessor = FeaturePreprocessor()
    X_train = preprocessor.fit_transform(train_df)
    y_train = train_df[TARGET_COL].values

    X_val = preprocessor.transform(val_df)
    y_val = val_df[TARGET_COL].values

    return X_train, y_train, X_val, y_val, preprocessor
