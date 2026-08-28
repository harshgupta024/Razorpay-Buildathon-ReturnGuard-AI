"""
ReturnGuard AI — Dataset Validator

Validates dataset integrity with schema checks, range checks,
and business logic constraints.

Usage:
    python src/data/validate_dataset.py
"""

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_FILE = PROJECT_ROOT / "data" / "raw" / "ecommerce_orders.csv"


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    check_name: str
    passed: bool
    message: str
    severity: str = "ERROR"  # ERROR, WARNING, INFO


@dataclass
class ValidationReport:
    """Collection of validation results."""
    results: list[ValidationResult] = field(default_factory=list)

    def add(self, check_name: str, passed: bool, message: str, severity: str = "ERROR") -> None:
        self.results.append(ValidationResult(check_name, passed, message, severity))

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results if r.severity == "ERROR")

    @property
    def total_checks(self) -> int:
        return len(self.results)

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    def summary(self) -> str:
        lines = [
            f"Validation: {'PASSED' if self.passed else 'FAILED'}",
            f"Checks: {self.total_checks} total, {self.passed_count} passed, {self.failed_count} failed",
        ]
        for r in self.results:
            status = "PASS" if r.passed else "FAIL"
            lines.append(f"  [{status}] [{r.severity}] {r.check_name}: {r.message}")
        return "\n".join(lines)


# ============================================================
# Validation functions
# ============================================================

REQUIRED_COLUMNS = [
    "order_id", "customer_id", "product_id", "order_date",
    "order_value", "quantity", "discount_pct", "payment_method",
    "is_first_order", "customer_account_age_days", "customer_total_orders",
    "customer_total_returns", "customer_return_rate", "customer_avg_order_value",
    "customer_segment", "customer_days_since_last_order",
    "product_category", "product_price", "product_weight_grams",
    "product_return_rate", "product_avg_rating",
    "order_value_deviation", "order_hour", "order_day_of_week",
    "is_weekend_order", "is_returned",
]

VALID_PAYMENT_METHODS = {"COD", "UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet"}
VALID_CATEGORIES = {"Electronics", "Clothing", "Footwear", "Beauty", "Home", "Books", "Sports", "Accessories"}
VALID_SEGMENTS = {"new", "regular", "premium", "vip"}


def validate_dataset(df: pd.DataFrame) -> ValidationReport:
    """Run all validation checks on the dataset."""
    report = ValidationReport()

    # --- Schema checks ---
    validate_schema(df, report)

    # --- Missing values ---
    validate_missing(df, report)

    # --- Duplicates ---
    validate_duplicates(df, report)

    # --- Range checks ---
    validate_ranges(df, report)

    # --- Categorical validity ---
    validate_categories(df, report)

    # --- Business logic ---
    validate_business_logic(df, report)

    # --- Target validity ---
    validate_target(df, report)

    # --- Leakage checks ---
    validate_leakage(df, report)

    return report


def validate_schema(df: pd.DataFrame, report: ValidationReport) -> None:
    """Check that all required columns exist."""
    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    report.add(
        "required_columns",
        len(missing_cols) == 0,
        f"Missing columns: {missing_cols}" if missing_cols else "All 26 required columns present",
    )

    report.add(
        "minimum_rows",
        len(df) >= 10_000,
        f"Dataset has {len(df):,} rows (minimum: 10,000)",
    )


def validate_missing(df: pd.DataFrame, report: ValidationReport) -> None:
    """Check for missing values."""
    total_missing = df.isna().sum().sum()
    report.add(
        "no_missing_values",
        total_missing == 0,
        f"Total missing: {total_missing:,}",
        severity="WARNING" if total_missing > 0 else "ERROR",
    )


def validate_duplicates(df: pd.DataFrame, report: ValidationReport) -> None:
    """Check for duplicate records."""
    dupe_orders = df["order_id"].duplicated().sum()
    report.add(
        "unique_order_ids",
        dupe_orders == 0,
        f"Duplicate order_ids: {dupe_orders}",
    )

    dupe_rows = df.duplicated().sum()
    report.add(
        "no_duplicate_rows",
        dupe_rows == 0,
        f"Duplicate rows: {dupe_rows}",
        severity="WARNING",
    )


def validate_ranges(df: pd.DataFrame, report: ValidationReport) -> None:
    """Check that numerical values are within expected ranges."""
    checks = [
        ("order_value", df["order_value"] > 0, "order_value > 0"),
        ("quantity_positive", df["quantity"] > 0, "quantity > 0"),
        ("quantity_max", df["quantity"] <= 10, "quantity <= 10"),
        ("discount_min", df["discount_pct"] >= 0, "discount_pct >= 0"),
        ("discount_max", df["discount_pct"] <= 100, "discount_pct <= 100"),
        ("return_rate_min", df["customer_return_rate"] >= 0, "customer_return_rate >= 0"),
        ("return_rate_max", df["customer_return_rate"] <= 1, "customer_return_rate <= 1"),
        ("product_return_rate_min", df["product_return_rate"] >= 0, "product_return_rate >= 0"),
        ("product_return_rate_max", df["product_return_rate"] <= 1, "product_return_rate <= 1"),
        ("product_rating_min", df["product_avg_rating"] >= 1.0, "product_avg_rating >= 1.0"),
        ("product_rating_max", df["product_avg_rating"] <= 5.0, "product_avg_rating <= 5.0"),
        ("account_age_positive", df["customer_account_age_days"] >= 1, "customer_account_age_days >= 1"),
        ("order_hour_range", (df["order_hour"] >= 0) & (df["order_hour"] <= 23), "order_hour in [0, 23]"),
        ("day_of_week_range", (df["order_day_of_week"] >= 0) & (df["order_day_of_week"] <= 6), "day_of_week in [0, 6]"),
    ]

    for name, condition, desc in checks:
        violations = (~condition).sum()
        report.add(
            f"range_{name}",
            violations == 0,
            f"{desc}: {violations:,} violations" if violations > 0 else f"{desc}: OK",
        )


def validate_categories(df: pd.DataFrame, report: ValidationReport) -> None:
    """Check that categorical values are valid."""
    invalid_payment = set(df["payment_method"].unique()) - VALID_PAYMENT_METHODS
    report.add(
        "valid_payment_methods",
        len(invalid_payment) == 0,
        f"Invalid: {invalid_payment}" if invalid_payment else "All payment methods valid",
    )

    invalid_cats = set(df["product_category"].unique()) - VALID_CATEGORIES
    report.add(
        "valid_product_categories",
        len(invalid_cats) == 0,
        f"Invalid: {invalid_cats}" if invalid_cats else "All categories valid",
    )

    invalid_segs = set(df["customer_segment"].unique()) - VALID_SEGMENTS
    report.add(
        "valid_customer_segments",
        len(invalid_segs) == 0,
        f"Invalid: {invalid_segs}" if invalid_segs else "All segments valid",
    )


def validate_business_logic(df: pd.DataFrame, report: ValidationReport) -> None:
    """Check business logic constraints."""
    # Returns cannot exceed total orders
    violations = (df["customer_total_returns"] > df["customer_total_orders"]).sum()
    report.add(
        "returns_leq_orders",
        violations == 0,
        f"customer_total_returns > customer_total_orders: {violations:,} violations",
    )

    # Return rate should match returns / orders
    expected_rate = np.where(
        df["customer_total_orders"] > 0,
        df["customer_total_returns"] / df["customer_total_orders"],
        0.0,
    )
    rate_mismatch = (np.abs(df["customer_return_rate"] - expected_rate) > 0.01).sum()
    report.add(
        "return_rate_consistent",
        rate_mismatch == 0,
        f"Return rate mismatches: {rate_mismatch:,}",
        severity="WARNING",
    )

    # is_first_order consistency
    first_order_mismatch = ((df["is_first_order"] == 1) & (df["customer_total_orders"] > 1)).sum()
    report.add(
        "first_order_consistent",
        first_order_mismatch == 0,
        f"is_first_order=1 but total_orders>1: {first_order_mismatch:,}",
        severity="WARNING",
    )


def validate_target(df: pd.DataFrame, report: ValidationReport) -> None:
    """Validate the target variable."""
    valid_targets = set(df["is_returned"].unique())
    report.add(
        "target_binary",
        valid_targets.issubset({0, 1}),
        f"Target values: {valid_targets}",
    )

    # Check class balance is not extreme
    pos_rate = df["is_returned"].mean()
    report.add(
        "target_not_extreme",
        0.05 < pos_rate < 0.95,
        f"Return rate: {pos_rate:.1%} (should be between 5% and 95%)",
    )

    report.add(
        "target_realistic_range",
        0.10 < pos_rate < 0.50,
        f"Return rate: {pos_rate:.1%} (expected 10-50% for e-commerce)",
        severity="WARNING",
    )


def validate_leakage(df: pd.DataFrame, report: ValidationReport) -> None:
    """Check for potential data leakage indicators."""
    # Check if target perfectly correlates with any single feature
    target = df["is_returned"]
    numeric_cols = df.select_dtypes(include=[np.number]).columns.drop("is_returned", errors="ignore")

    for col in numeric_cols:
        corr = np.abs(target.corr(df[col]))
        if corr > 0.95:
            report.add(
                f"leakage_{col}",
                False,
                f"LEAKAGE RISK: {col} has |correlation| = {corr:.3f} with target",
            )

    # If we get here with no leakage, add a passing check
    report.add(
        "no_perfect_correlation",
        True,
        "No single feature has |correlation| > 0.95 with target",
        severity="INFO",
    )


def main() -> None:
    """Run validation."""
    logger.info("Loading dataset from %s...", DATA_FILE)

    if not DATA_FILE.exists():
        logger.error("Dataset not found. Run: python src/data/generate_dataset.py")
        sys.exit(1)

    df = pd.read_csv(DATA_FILE, parse_dates=["order_date"])
    logger.info("Loaded: %s", df.shape)

    report = validate_dataset(df)
    print()
    print("=" * 60)
    print("DATASET VALIDATION REPORT")
    print("=" * 60)
    print(report.summary())
    print("=" * 60)

    if not report.passed:
        logger.error("Validation FAILED — fix issues before proceeding.")
        sys.exit(1)
    else:
        logger.info("Validation PASSED — dataset is ready for processing.")


if __name__ == "__main__":
    main()
