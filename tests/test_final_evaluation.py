"""
Tests for Phase 16: Final Held-Out Test Split Evaluation Artifacts & Benchmarks.
"""

import json
import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

REPORTS_DIR = PROJECT_ROOT / "reports"
JSON_PATH = REPORTS_DIR / "final_test_evaluation.json"
REPORT_PATH = REPORTS_DIR / "final-test-evaluation-report.md"
FIGURE_PATH = REPORTS_DIR / "figures" / "14_final_test_evaluation.png"


@pytest.fixture(scope="module")
def test_evaluation_json():
    if not JSON_PATH.exists():
        from src.ml.evaluate_test import run_final_test_evaluation
        run_final_test_evaluation()
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class TestFinalEvaluationArtifacts:
    """Test suite verifying final evaluation benchmarks and artifacts."""

    def test_artifacts_exist(self):
        assert JSON_PATH.exists(), f"Missing {JSON_PATH}"
        assert REPORT_PATH.exists(), f"Missing {REPORT_PATH}"
        assert FIGURE_PATH.exists(), f"Missing {FIGURE_PATH}"
        assert FIGURE_PATH.stat().st_size > 10000

    def test_test_discrimination_benchmarks(self, test_evaluation_json):
        stat = test_evaluation_json["statistical_metrics"]
        assert stat["roc_auc"] >= 0.70, f"Test ROC-AUC too low: {stat['roc_auc']}"
        assert stat["pr_auc"] >= 0.45, f"Test PR-AUC too low: {stat['pr_auc']}"
        assert stat["single_record_latency_ms"] < 5.0, "Latency SLA violated"

    def test_test_calibration_benchmarks(self, test_evaluation_json):
        stat = test_evaluation_json["statistical_metrics"]
        assert stat["expected_calibration_error_ece"] <= 0.05, f"ECE too high: {stat['expected_calibration_error_ece']}"
        assert stat["brier_score"] <= 0.20, f"Brier score too high: {stat['brier_score']}"

    def test_financial_savings_benchmarks(self, test_evaluation_json):
        fin = test_evaluation_json["financial_performance_at_optimal_threshold"]
        assert fin["net_savings_vs_do_nothing_inr"] > 1000000.0  # > Rs. 10 Lakhs
        assert fin["net_savings_vs_naive_ml_inr"] > 500000.0    # > Rs. 5 Lakhs
        assert fin["recall_catch_rate"] >= 0.75                  # >= 75% catch rate

    def test_report_contents(self):
        content = REPORT_PATH.read_text(encoding="utf-8")
        assert "Final Held-Out Test Evaluation Benchmark" in content
        assert "Discrimination Power" in content
        assert "Asymmetric Business Cost Model" in content
        assert "Multi-Tier Risk Segment Verification" in content
