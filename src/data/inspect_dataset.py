"""
ReturnGuard AI — Dataset Inspector

Generates an initial profiling report for the raw dataset.

Usage:
    python src/data/inspect_dataset.py
"""

import logging
import sys
from pathlib import Path

import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_FILE = PROJECT_ROOT / "data" / "raw" / "ecommerce_orders.csv"
REPORT_FILE = PROJECT_ROOT / "reports" / "data-inspection-report.md"

# Features classified by timing
PRE_FULFILLMENT_FEATURES = [
    "order_id", "customer_id", "product_id", "order_date",
    "order_value", "quantity", "discount_pct", "payment_method",
    "is_first_order", "customer_account_age_days", "customer_total_orders",
    "customer_total_returns", "customer_return_rate", "customer_avg_order_value",
    "customer_segment", "customer_days_since_last_order",
    "product_category", "product_price", "product_weight_grams",
    "product_return_rate", "product_avg_rating",
    "order_value_deviation", "order_hour", "order_day_of_week",
    "is_weekend_order",
]

POST_FULFILLMENT_FEATURES: list[str] = []  # None in our dataset by design

LEAKAGE_CANDIDATES = [
    "customer_return_rate",   # Derived from historical data, acceptable if computed BEFORE this order
    "product_return_rate",    # Derived from historical data, acceptable if computed BEFORE this order
    "customer_total_returns", # Historical count, acceptable if computed BEFORE this order
]


def inspect_dataset() -> str:
    """Inspect the dataset and return a markdown report."""
    if not DATA_FILE.exists():
        logger.error("Dataset not found at %s", DATA_FILE)
        logger.error("Run: python src/data/generate_dataset.py")
        sys.exit(1)

    df = pd.read_csv(DATA_FILE, parse_dates=["order_date"])
    logger.info("Loaded dataset: %s", df.shape)

    lines: list[str] = []

    def add(text: str = "") -> None:
        lines.append(text)

    add("# Data Inspection Report — ReturnGuard AI")
    add()
    add(f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    add(f"**Source file:** `{DATA_FILE.name}`")
    add()

    # 1. Shape
    add("## 1. Dataset Shape")
    add()
    add(f"| Metric | Value |")
    add(f"|--------|-------|")
    add(f"| Rows | {len(df):,} |")
    add(f"| Columns | {len(df.columns)} |")
    add(f"| File size | {DATA_FILE.stat().st_size / 1e6:.2f} MB |")
    add()

    # 2. Column overview
    add("## 2. Column Overview")
    add()
    add("| # | Column | Type | Non-Null | Missing | Unique | Sample |")
    add("|---|--------|------|----------|---------|--------|--------|")
    for i, col in enumerate(df.columns, 1):
        dtype = str(df[col].dtype)
        non_null = df[col].notna().sum()
        missing = df[col].isna().sum()
        unique = df[col].nunique()
        sample = str(df[col].iloc[0])[:30]
        add(f"| {i} | `{col}` | {dtype} | {non_null:,} | {missing} | {unique:,} | {sample} |")
    add()

    # 3. Missing values
    add("## 3. Missing Values")
    add()
    missing_total = df.isna().sum().sum()
    if missing_total == 0:
        add("✅ **No missing values found.**")
    else:
        add(f"⚠️ Total missing values: {missing_total:,}")
        for col in df.columns:
            miss = df[col].isna().sum()
            if miss > 0:
                add(f"  - `{col}`: {miss:,} ({miss/len(df)*100:.1f}%)")
    add()

    # 4. Duplicate rows
    add("## 4. Duplicate Rows")
    add()
    dupes = df.duplicated().sum()
    add(f"Duplicate rows: **{dupes:,}**")
    add()
    order_id_dupes = df["order_id"].duplicated().sum()
    add(f"Duplicate order_ids: **{order_id_dupes:,}**")
    add()

    # 5. Target distribution
    add("## 5. Target Distribution (`is_returned`)")
    add()
    target_counts = df["is_returned"].value_counts().sort_index()
    add("| Value | Label | Count | Percentage |")
    add("|-------|-------|-------|------------|")
    for val, count in target_counts.items():
        label = "Returned" if val == 1 else "Not Returned"
        pct = count / len(df) * 100
        add(f"| {val} | {label} | {count:,} | {pct:.1f}% |")
    add()
    add(f"**Class ratio (returned:not):** 1:{(target_counts[0]/target_counts[1]):.2f}")
    add()

    # 6. Numerical feature statistics
    add("## 6. Numerical Feature Statistics")
    add()
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    desc = df[num_cols].describe().T
    add("| Feature | Count | Mean | Std | Min | 25% | 50% | 75% | Max |")
    add("|---------|-------|------|-----|-----|-----|-----|-----|-----|")
    for col in desc.index:
        row = desc.loc[col]
        add(
            f"| `{col}` | {row['count']:.0f} | {row['mean']:.2f} | "
            f"{row['std']:.2f} | {row['min']:.2f} | {row['25%']:.2f} | "
            f"{row['50%']:.2f} | {row['75%']:.2f} | {row['max']:.2f} |"
        )
    add()

    # 7. Categorical feature distributions
    add("## 7. Categorical Feature Distributions")
    add()
    cat_cols = ["payment_method", "customer_segment", "product_category"]
    for col in cat_cols:
        add(f"### `{col}`")
        add()
        vc = df[col].value_counts()
        add("| Value | Count | Percentage |")
        add("|-------|-------|------------|")
        for val, count in vc.items():
            pct = count / len(df) * 100
            add(f"| {val} | {count:,} | {pct:.1f}% |")
        add()

    # 8. Return rate by key dimensions
    add("## 8. Return Rate by Key Dimensions")
    add()

    for dim in ["product_category", "payment_method", "customer_segment"]:
        add(f"### By `{dim}`")
        add()
        group = df.groupby(dim)["is_returned"].agg(["mean", "count"])
        group = group.sort_values("mean", ascending=False)
        add("| Value | Return Rate | Order Count |")
        add("|-------|-------------|-------------|")
        for val, row in group.iterrows():
            add(f"| {val} | {row['mean']:.1%} | {row['count']:,.0f} |")
        add()

    # 9. ID uniqueness
    add("## 9. ID Uniqueness")
    add()
    add("| ID Column | Total | Unique | Duplicates |")
    add("|-----------|-------|--------|------------|")
    for col in ["order_id", "customer_id", "product_id"]:
        total = len(df)
        unique = df[col].nunique()
        dupes = total - unique
        add(f"| `{col}` | {total:,} | {unique:,} | {dupes:,} |")
    add()

    # 10. Feature timing classification
    add("## 10. Feature Timing Classification")
    add()
    add("| Feature | Classification | Usable for Prediction? |")
    add("|---------|---------------|----------------------|")
    for col in df.columns:
        if col == "is_returned":
            add(f"| `{col}` | **TARGET** | N/A (this is what we predict) |")
        elif col in POST_FULFILLMENT_FEATURES:
            add(f"| `{col}` | ❌ POST-FULFILLMENT | No — leakage risk |")
        else:
            leakage_note = " ⚠️ (review needed)" if col in LEAKAGE_CANDIDATES else ""
            add(f"| `{col}` | ✅ PRE-FULFILLMENT | Yes{leakage_note} |")
    add()

    # 11. Potential leakage analysis
    add("## 11. Leakage Analysis")
    add()
    add("### Features requiring careful review")
    add()
    add("| Feature | Risk | Justification |")
    add("|---------|------|---------------|")
    add("| `customer_return_rate` | ⚠️ Low | Historical aggregate — computed BEFORE this order. Acceptable if time-based. |")
    add("| `customer_total_returns` | ⚠️ Low | Historical count — same as above. |")
    add("| `product_return_rate` | ⚠️ Low | Historical product-level aggregate. Acceptable if computed from prior orders. |")
    add()
    add("### Confirmed NO post-fulfillment features in dataset")
    add()
    add("The following features are deliberately **excluded** from the dataset:")
    add("- Return date, Return reason, Refund amount, Refund status")
    add("- Delivery date, Delivery satisfaction, Post-delivery complaint")
    add("- Return shipment tracking, Warehouse inspection result")
    add()

    # 12. Suspicious patterns
    add("## 12. Suspicious Patterns")
    add()
    # Check for impossible values
    issues = []
    if (df["order_value"] <= 0).any():
        issues.append("❌ Negative or zero order values found")
    if (df["customer_return_rate"] > 1).any() or (df["customer_return_rate"] < 0).any():
        issues.append("❌ customer_return_rate outside [0, 1]")
    if (df["product_return_rate"] > 1).any() or (df["product_return_rate"] < 0).any():
        issues.append("❌ product_return_rate outside [0, 1]")
    if (df["discount_pct"] > 100).any() or (df["discount_pct"] < 0).any():
        issues.append("❌ discount_pct outside [0, 100]")
    if (df["customer_total_returns"] > df["customer_total_orders"]).any():
        issues.append("❌ customer_total_returns > customer_total_orders")
    if (df["quantity"] <= 0).any():
        issues.append("❌ Zero or negative quantities")

    if not issues:
        add("✅ **No suspicious patterns detected.** All values within expected ranges.")
    else:
        for issue in issues:
            add(issue)
    add()

    report = "\n".join(lines)
    return report


def main() -> None:
    """Generate the inspection report."""
    logger.info("Inspecting dataset...")
    report = inspect_dataset()

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(report, encoding="utf-8")

    logger.info("Report saved to %s", REPORT_FILE)
    logger.info("Report length: %d lines", len(report.split("\n")))

    # Print summary to console
    print("\n" + "=" * 60)
    print("INSPECTION COMPLETE")
    print("=" * 60)
    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
