"""
Tests for Phase 3: Exploratory Data Analysis.
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
REPORT_FILE = PROJECT_ROOT / "reports" / "eda-report.md"


class TestEDAOutputs:
    """Verify EDA outputs exist and are valid."""

    EXPECTED_FIGURES = [
        "01_target_distribution.png",
        "02_numerical_distributions.png",
        "03_correlation_matrix.png",
        "04_return_rate_by_category.png",
        "05_return_rate_by_price_band.png",
        "06_return_rate_by_payment.png",
        "07_return_rate_by_segment.png",
        "08_customer_behavior_patterns.png",
        "09_feature_importance_proxy.png",
        "10_temporal_patterns.png",
    ]

    def test_eda_report_exists(self):
        assert REPORT_FILE.exists(), f"EDA report not found at {REPORT_FILE}"

    def test_eda_report_has_all_sections(self):
        content = REPORT_FILE.read_text(encoding="utf-8")
        required_headings = [
            "Target Distribution",
            "Numerical Feature Distributions",
            "Feature Correlations",
            "Return Rate by Product Category",
            "Return Rate by Order Value Band",
            "Return Rate by Payment Method",
            "Return Rate by Customer Segment",
            "Customer Behavioral Risk Patterns",
            "Feature Importance",
            "Temporal Patterns",
            "Summary of Key EDA Findings",
            "Limitations and Biases",
        ]
        for heading in required_headings:
            assert heading in content, f"Missing section: {heading}"

    def test_all_figures_generated(self):
        for fig_name in self.EXPECTED_FIGURES:
            fig_path = FIGURES_DIR / fig_name
            assert fig_path.exists(), f"Missing figure: {fig_name}"

    def test_figures_are_non_empty(self):
        for fig_name in self.EXPECTED_FIGURES:
            fig_path = FIGURES_DIR / fig_name
            if fig_path.exists():
                assert fig_path.stat().st_size > 5000, f"Figure {fig_name} is suspiciously small"

    def test_report_mentions_no_test_set_usage(self):
        content = REPORT_FILE.read_text(encoding="utf-8")
        assert "test set was NOT used" in content, "EDA report should declare no test-set contamination"
