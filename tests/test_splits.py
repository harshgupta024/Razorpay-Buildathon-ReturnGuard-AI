"""
Tests for Phase 4: Train / Validation / Test Split.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

SPLITS_DIR = PROJECT_ROOT / "data" / "splits"
TRAIN_PATH = SPLITS_DIR / "train.csv"
VAL_PATH = SPLITS_DIR / "val.csv"
TEST_PATH = SPLITS_DIR / "test.csv"
META_PATH = SPLITS_DIR / "split_metadata.json"


@pytest.fixture(scope="module")
def splits():
    for p in [TRAIN_PATH, VAL_PATH, TEST_PATH]:
        if not p.exists():
            pytest.skip("Splits not found. Run: python src/data/split_dataset.py")
    return {
        "train": pd.read_csv(TRAIN_PATH),
        "val": pd.read_csv(VAL_PATH),
        "test": pd.read_csv(TEST_PATH),
    }


class TestSplitSizes:
    def test_total_rows_preserved(self, splits):
        total = len(splits["train"]) + len(splits["val"]) + len(splits["test"])
        assert total == 100_000

    def test_train_size_approximately_70_pct(self, splits):
        ratio = len(splits["train"]) / 100_000
        assert 0.69 <= ratio <= 0.71

    def test_val_size_approximately_15_pct(self, splits):
        ratio = len(splits["val"]) / 100_000
        assert 0.14 <= ratio <= 0.16

    def test_test_size_approximately_15_pct(self, splits):
        ratio = len(splits["test"]) / 100_000
        assert 0.14 <= ratio <= 0.16


class TestNoLeakage:
    def test_no_train_val_overlap(self, splits):
        overlap = set(splits["train"]["order_id"]) & set(splits["val"]["order_id"])
        assert len(overlap) == 0, f"Train-Val overlap: {len(overlap)} order_ids"

    def test_no_train_test_overlap(self, splits):
        overlap = set(splits["train"]["order_id"]) & set(splits["test"]["order_id"])
        assert len(overlap) == 0, f"Train-Test overlap: {len(overlap)} order_ids"

    def test_no_val_test_overlap(self, splits):
        overlap = set(splits["val"]["order_id"]) & set(splits["test"]["order_id"])
        assert len(overlap) == 0, f"Val-Test overlap: {len(overlap)} order_ids"


class TestStratification:
    def test_target_rate_preserved_in_train(self, splits):
        rate = splits["train"]["is_returned"].mean()
        assert 0.25 <= rate <= 0.30, f"Train return rate {rate:.3f} outside [0.25, 0.30]"

    def test_target_rate_preserved_in_val(self, splits):
        rate = splits["val"]["is_returned"].mean()
        assert 0.25 <= rate <= 0.30, f"Val return rate {rate:.3f} outside [0.25, 0.30]"

    def test_target_rate_preserved_in_test(self, splits):
        rate = splits["test"]["is_returned"].mean()
        assert 0.25 <= rate <= 0.30, f"Test return rate {rate:.3f} outside [0.25, 0.30]"

    def test_max_stratification_deviation_under_1_pct(self, splits):
        rates = [s["is_returned"].mean() for s in splits.values()]
        overall = sum(len(s) * s["is_returned"].mean() for s in splits.values()) / sum(len(s) for s in splits.values())
        max_dev = max(abs(r - overall) for r in rates)
        assert max_dev < 0.01, f"Max stratification deviation {max_dev:.4f} exceeds 1%"


class TestMetadata:
    def test_metadata_file_exists(self):
        assert META_PATH.exists()

    def test_metadata_contains_required_fields(self):
        with open(META_PATH) as f:
            meta = json.load(f)
        required = ["random_seed", "split_ratios", "split_sizes", "target_distribution",
                     "leakage_check", "split_hashes"]
        for key in required:
            assert key in meta, f"Missing metadata field: {key}"

    def test_metadata_leakage_passed(self):
        with open(META_PATH) as f:
            meta = json.load(f)
        assert meta["leakage_check"] == "PASSED"


class TestColumnConsistency:
    def test_all_splits_have_same_columns(self, splits):
        train_cols = set(splits["train"].columns)
        val_cols = set(splits["val"].columns)
        test_cols = set(splits["test"].columns)
        assert train_cols == val_cols == test_cols
