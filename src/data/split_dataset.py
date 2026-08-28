"""
ReturnGuard AI — Stratified Train / Validation / Test Splitter

Creates reproducible, stratified data splits preserving target distribution.
Ensures zero data leakage between splits.

Usage:
    python src/data/split_dataset.py

Output:
    data/splits/train.csv
    data/splits/val.csv
    data/splits/test.csv
    data/splits/split_metadata.json
"""

import hashlib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import MLConfig, PROJECT_ROOT as PROJ_ROOT

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DATA_PATH = PROJ_ROOT / "data" / "raw" / "ecommerce_orders.csv"
SPLITS_DIR = PROJ_ROOT / "data" / "splits"

ml_config = MLConfig()
RANDOM_SEED = ml_config.random_seed
TRAIN_SIZE = ml_config.train_size
VAL_SIZE = ml_config.val_size
TEST_SIZE = ml_config.test_size
TARGET_COL = "is_returned"


def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def validate_split_ratios() -> None:
    """Validate that split ratios sum to 1.0."""
    total = TRAIN_SIZE + VAL_SIZE + TEST_SIZE
    assert abs(total - 1.0) < 1e-6, f"Split ratios must sum to 1.0, got {total}"


def create_stratified_splits(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create stratified train/val/test splits."""
    # First split: separate test set
    # train+val = TRAIN_SIZE + VAL_SIZE, test = TEST_SIZE
    train_val, test = train_test_split(
        df,
        test_size=TEST_SIZE,
        random_state=RANDOM_SEED,
        stratify=df[TARGET_COL],
    )

    # Second split: separate train and val from train_val
    # val proportion within train_val = VAL_SIZE / (TRAIN_SIZE + VAL_SIZE)
    val_ratio = VAL_SIZE / (TRAIN_SIZE + VAL_SIZE)
    train, val = train_test_split(
        train_val,
        test_size=val_ratio,
        random_state=RANDOM_SEED,
        stratify=train_val[TARGET_COL],
    )

    return train, val, test


def validate_no_leakage(
    train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame
) -> list[str]:
    """Verify zero row overlap between splits."""
    issues = []

    train_ids = set(train["order_id"])
    val_ids = set(val["order_id"])
    test_ids = set(test["order_id"])

    train_val_overlap = train_ids & val_ids
    train_test_overlap = train_ids & test_ids
    val_test_overlap = val_ids & test_ids

    if train_val_overlap:
        issues.append(f"LEAKAGE: {len(train_val_overlap)} order_ids in both train and val")
    if train_test_overlap:
        issues.append(f"LEAKAGE: {len(train_test_overlap)} order_ids in both train and test")
    if val_test_overlap:
        issues.append(f"LEAKAGE: {len(val_test_overlap)} order_ids in both val and test")

    # Verify total row count
    total = len(train) + len(val) + len(test)
    expected = len(train_ids | val_ids | test_ids)
    if total != expected:
        issues.append(f"Row count mismatch: {total} vs {expected} unique IDs")

    return issues


def validate_stratification(
    df: pd.DataFrame, train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame
) -> dict:
    """Verify target distribution is preserved across splits."""
    overall_rate = df[TARGET_COL].mean()
    train_rate = train[TARGET_COL].mean()
    val_rate = val[TARGET_COL].mean()
    test_rate = test[TARGET_COL].mean()

    return {
        "overall": round(overall_rate, 4),
        "train": round(train_rate, 4),
        "val": round(val_rate, 4),
        "test": round(test_rate, 4),
        "max_deviation": round(
            max(abs(train_rate - overall_rate), abs(val_rate - overall_rate), abs(test_rate - overall_rate)), 4
        ),
    }


def generate_metadata(
    df: pd.DataFrame, train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame,
    stratification: dict, leakage_issues: list[str],
) -> dict:
    """Generate split metadata for reproducibility."""
    return {
        "generated_at": datetime.now().isoformat(),
        "random_seed": RANDOM_SEED,
        "source_file": str(RAW_DATA_PATH),
        "source_sha256": compute_sha256(RAW_DATA_PATH),
        "split_ratios": {
            "train": TRAIN_SIZE,
            "val": VAL_SIZE,
            "test": TEST_SIZE,
        },
        "split_sizes": {
            "total": len(df),
            "train": len(train),
            "val": len(val),
            "test": len(test),
        },
        "target_distribution": stratification,
        "leakage_check": "PASSED" if not leakage_issues else "FAILED",
        "leakage_issues": leakage_issues,
        "split_files": {
            "train": "train.csv",
            "val": "val.csv",
            "test": "test.csv",
        },
        "split_hashes": {},  # Filled after saving
    }


def main() -> None:
    """Execute the split pipeline."""
    logger.info("=" * 60)
    logger.info("ReturnGuard AI --- Train / Validation / Test Split")
    logger.info("=" * 60)

    # Check for existing splits
    train_path = SPLITS_DIR / "train.csv"
    val_path = SPLITS_DIR / "val.csv"
    test_path = SPLITS_DIR / "test.csv"

    if train_path.exists() and val_path.exists() and test_path.exists():
        logger.info("Splits already exist. To regenerate, delete data/splits/*.csv")
        for name, path in [("Train", train_path), ("Val", val_path), ("Test", test_path)]:
            df_check = pd.read_csv(path)
            logger.info("  %s: %d rows, return_rate=%.2f%%", name, len(df_check), df_check[TARGET_COL].mean() * 100)
        return

    # Validate
    validate_split_ratios()
    logger.info("Split ratios: train=%.0f%%, val=%.0f%%, test=%.0f%%",
                TRAIN_SIZE * 100, VAL_SIZE * 100, TEST_SIZE * 100)

    # Load
    df = pd.read_csv(RAW_DATA_PATH, parse_dates=["order_date"])
    logger.info("Loaded %d records from %s", len(df), RAW_DATA_PATH.name)

    # Split
    train, val, test = create_stratified_splits(df)
    logger.info("Split sizes: train=%d, val=%d, test=%d", len(train), len(val), len(test))

    # Validate leakage
    leakage_issues = validate_no_leakage(train, val, test)
    if leakage_issues:
        for issue in leakage_issues:
            logger.error(issue)
        sys.exit(1)
    logger.info("Leakage check: PASSED (zero overlap)")

    # Validate stratification
    strat = validate_stratification(df, train, val, test)
    logger.info("Stratification check:")
    logger.info("  Overall: %.2f%%, Train: %.2f%%, Val: %.2f%%, Test: %.2f%%",
                strat["overall"] * 100, strat["train"] * 100, strat["val"] * 100, strat["test"] * 100)
    logger.info("  Max deviation from overall: %.4f", strat["max_deviation"])

    # Save splits
    SPLITS_DIR.mkdir(parents=True, exist_ok=True)
    train.to_csv(train_path, index=False)
    val.to_csv(val_path, index=False)
    test.to_csv(test_path, index=False)
    logger.info("Splits saved to %s", SPLITS_DIR)

    # Generate and save metadata
    metadata = generate_metadata(df, train, val, test, strat, leakage_issues)
    metadata["split_hashes"] = {
        "train": compute_sha256(train_path),
        "val": compute_sha256(val_path),
        "test": compute_sha256(test_path),
    }

    meta_path = SPLITS_DIR / "split_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2, default=str)
    logger.info("Metadata saved to %s", meta_path)

    # Summary
    logger.info("=" * 60)
    logger.info("SPLIT COMPLETE")
    logger.info("=" * 60)
    logger.info("  Train: %d rows (%.1f%%) -> %s", len(train), len(train) / len(df) * 100, train_path.name)
    logger.info("  Val:   %d rows (%.1f%%) -> %s", len(val), len(val) / len(df) * 100, val_path.name)
    logger.info("  Test:  %d rows (%.1f%%) -> %s", len(test), len(test) / len(df) * 100, test_path.name)
    logger.info("")
    logger.info("WARNING: The test set is LOCKED until final held-out evaluation.")
    logger.info("Do NOT use test.csv for feature selection, tuning, or EDA.")


if __name__ == "__main__":
    main()
