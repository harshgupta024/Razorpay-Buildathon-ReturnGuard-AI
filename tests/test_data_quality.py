"""
Unit and Integration tests for Phase 2: Data Quality & Validation Pipeline.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.data_quality import DataQualityAuditor, RAW_DATA_PATH, REPORT_PATH


@pytest.fixture(scope="module")
def auditor():
    if not RAW_DATA_PATH.exists():
        pytest.skip(f"Dataset {RAW_DATA_PATH} not found.")
    auditor_instance = DataQualityAuditor(RAW_DATA_PATH)
    auditor_instance.run_all()
    return auditor_instance


class TestDataQualityPipeline:
    """Test suite verifying all Data Quality checks and report generation."""

    def test_auditor_executed_all_checks(self, auditor):
        assert len(auditor.checks) >= 25, f"Expected at least 25 quality checks, got {len(auditor.checks)}"

    def test_zero_failed_checks(self, auditor):
        failed_checks = [c for c in auditor.checks if c.status == "FAIL"]
        assert len(failed_checks) == 0, f"Quality checks failed: {[c.name for c in failed_checks]}"

    def test_schema_checks_passed(self, auditor):
        schema_checks = [c for c in auditor.checks if c.category == "Schema"]
        assert len(schema_checks) >= 2
        assert all(c.status == "PASS" for c in schema_checks)

    def test_completeness_and_uniqueness_checks(self, auditor):
        comp_checks = [c for c in auditor.checks if c.category in ["Completeness", "Uniqueness"]]
        assert len(comp_checks) >= 3
        assert all(c.status == "PASS" for c in comp_checks)

    def test_business_logic_invariants(self, auditor):
        biz_checks = [c for c in auditor.checks if c.category == "Business Logic"]
        assert len(biz_checks) >= 3
        assert all(c.status == "PASS" for c in biz_checks)

    def test_target_and_leakage_safeguards(self, auditor):
        leak_checks = [c for c in auditor.checks if c.category == "Target & Leakage"]
        assert len(leak_checks) >= 2
        assert all(c.status == "PASS" for c in leak_checks)

    def test_markdown_report_generation(self, auditor):
        report = auditor.generate_markdown_report()
        assert "# Data Quality & Validation Report — ReturnGuard AI" in report
        assert "HEALTHY / PRODUCTION-READY" in report
        assert "Statistical Distribution & Anomaly Profiles" in report
        assert "Pre-Fulfillment Leakage Prevention Audit" in report

    def test_report_file_exists(self):
        assert REPORT_PATH.exists(), f"Report file {REPORT_PATH} was not generated."
        content = REPORT_PATH.read_text(encoding="utf-8")
        assert len(content) > 500, "Report file is suspiciously small or empty."
