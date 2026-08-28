"""
Tests for ReturnGuard AI data module.

Tests dataset generation, inspection, and validation.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATA_FILE = PROJECT_ROOT / "data" / "raw" / "ecommerce_orders.csv"


@pytest.fixture(scope="module")
def dataset() -> pd.DataFrame:
    """Load the dataset once for all tests."""
    if not DATA_FILE.exists():
        pytest.skip("Dataset not generated. Run: python src/data/generate_dataset.py")
    return pd.read_csv(DATA_FILE, parse_dates=["order_date"])


class TestDatasetShape:
    """Test dataset dimensions."""

    def test_has_sufficient_rows(self, dataset: pd.DataFrame):
        assert len(dataset) >= 50_000, f"Expected >= 50,000 rows, got {len(dataset)}"

    def test_has_correct_column_count(self, dataset: pd.DataFrame):
        assert len(dataset.columns) == 26, f"Expected 26 columns, got {len(dataset.columns)}"

    def test_no_missing_values(self, dataset: pd.DataFrame):
        total_missing = dataset.isna().sum().sum()
        assert total_missing == 0, f"Found {total_missing} missing values"


class TestTargetVariable:
    """Test the is_returned target variable."""

    def test_target_is_binary(self, dataset: pd.DataFrame):
        unique_vals = set(dataset["is_returned"].unique())
        assert unique_vals == {0, 1}, f"Target has values: {unique_vals}"

    def test_return_rate_realistic(self, dataset: pd.DataFrame):
        rate = dataset["is_returned"].mean()
        assert 0.10 < rate < 0.50, f"Return rate {rate:.1%} outside realistic range"

    def test_both_classes_present(self, dataset: pd.DataFrame):
        counts = dataset["is_returned"].value_counts()
        assert len(counts) == 2
        assert counts.min() > 1000, "Minority class has too few samples"


class TestIDUniqueness:
    """Test identifier uniqueness."""

    def test_order_ids_unique(self, dataset: pd.DataFrame):
        dupes = dataset["order_id"].duplicated().sum()
        assert dupes == 0, f"Found {dupes} duplicate order IDs"

    def test_multiple_customers(self, dataset: pd.DataFrame):
        n_customers = dataset["customer_id"].nunique()
        assert n_customers > 1000, f"Only {n_customers} unique customers"

    def test_multiple_products(self, dataset: pd.DataFrame):
        n_products = dataset["product_id"].nunique()
        assert n_products >= 20, f"Only {n_products} unique products"


class TestValueRanges:
    """Test that values are within expected ranges."""

    def test_order_value_positive(self, dataset: pd.DataFrame):
        assert (dataset["order_value"] > 0).all(), "Found non-positive order values"

    def test_quantity_positive(self, dataset: pd.DataFrame):
        assert (dataset["quantity"] > 0).all(), "Found non-positive quantities"

    def test_discount_range(self, dataset: pd.DataFrame):
        assert (dataset["discount_pct"] >= 0).all()
        assert (dataset["discount_pct"] <= 100).all()

    def test_customer_return_rate_range(self, dataset: pd.DataFrame):
        assert (dataset["customer_return_rate"] >= 0).all()
        assert (dataset["customer_return_rate"] <= 1).all()

    def test_product_return_rate_range(self, dataset: pd.DataFrame):
        assert (dataset["product_return_rate"] >= 0).all()
        assert (dataset["product_return_rate"] <= 1).all()

    def test_product_rating_range(self, dataset: pd.DataFrame):
        assert (dataset["product_avg_rating"] >= 1.0).all()
        assert (dataset["product_avg_rating"] <= 5.0).all()


class TestBusinessLogic:
    """Test business logic constraints."""

    def test_returns_leq_orders(self, dataset: pd.DataFrame):
        violations = (dataset["customer_total_returns"] > dataset["customer_total_orders"]).sum()
        assert violations == 0, f"{violations} rows have returns > orders"

    def test_valid_payment_methods(self, dataset: pd.DataFrame):
        valid = {"COD", "UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet"}
        actual = set(dataset["payment_method"].unique())
        assert actual.issubset(valid), f"Invalid methods: {actual - valid}"

    def test_valid_categories(self, dataset: pd.DataFrame):
        valid = {"Electronics", "Clothing", "Footwear", "Beauty", "Home", "Books", "Sports", "Accessories"}
        actual = set(dataset["product_category"].unique())
        assert actual.issubset(valid), f"Invalid categories: {actual - valid}"

    def test_valid_segments(self, dataset: pd.DataFrame):
        valid = {"new", "regular", "premium", "vip"}
        actual = set(dataset["customer_segment"].unique())
        assert actual.issubset(valid), f"Invalid segments: {actual - valid}"


class TestNoLeakage:
    """Test that no post-fulfillment features are present."""

    FORBIDDEN_COLUMNS = [
        "return_date", "return_reason", "refund_amount", "refund_status",
        "delivery_date", "delivery_satisfaction", "post_delivery_complaint",
        "return_shipment_tracking", "warehouse_inspection",
    ]

    def test_no_post_fulfillment_columns(self, dataset: pd.DataFrame):
        present = [col for col in self.FORBIDDEN_COLUMNS if col in dataset.columns]
        assert len(present) == 0, f"Post-fulfillment columns found: {present}"

    def test_no_perfect_target_correlation(self, dataset: pd.DataFrame):
        """No single feature should perfectly predict the target."""
        target = dataset["is_returned"]
        numeric_cols = dataset.select_dtypes(include=[np.number]).columns.drop(
            "is_returned", errors="ignore"
        )
        for col in numeric_cols:
            corr = abs(target.corr(dataset[col]))
            assert corr < 0.95, f"Feature {col} has suspiciously high correlation: {corr:.3f}"


class TestValidation:
    """Test the validation module."""

    def test_validator_passes(self, dataset: pd.DataFrame):
        from src.data.validate_dataset import validate_dataset
        report = validate_dataset(dataset)
        assert report.passed, f"Validation failed:\n{report.summary()}"

    def test_validator_returns_all_checks(self, dataset: pd.DataFrame):
        from src.data.validate_dataset import validate_dataset
        report = validate_dataset(dataset)
        assert report.total_checks >= 20, f"Expected >= 20 checks, got {report.total_checks}"


class TestReproducibility:
    """Test that generation is reproducible."""

    def test_same_seed_same_output(self):
        """Generating with the same seed should produce identical data."""
        from src.data.generate_dataset import generate_products, generate_customers

        rng1 = np.random.default_rng(42)
        products1 = generate_products(rng1)

        rng2 = np.random.default_rng(42)
        products2 = generate_products(rng2)

        pd.testing.assert_frame_equal(products1, products2)
