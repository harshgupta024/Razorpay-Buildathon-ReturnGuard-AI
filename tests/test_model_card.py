"""
Tests for Phase 17: Model Card & Responsible AI Governance Documentation.
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DOCS_MODEL_CARD = PROJECT_ROOT / "docs" / "model-card.md"
REPORTS_MODEL_CARD = PROJECT_ROOT / "reports" / "model-card.md"


class TestModelCardSpecification:
    """Test suite verifying Model Card standards compliance and ethical AI guardrails."""

    def test_model_card_files_exist(self):
        assert DOCS_MODEL_CARD.exists(), "docs/model-card.md not found"
        assert REPORTS_MODEL_CARD.exists(), "reports/model-card.md not found"

    def test_required_model_card_sections(self):
        content = DOCS_MODEL_CARD.read_text(encoding="utf-8")

        required_sections = [
            "Model Details",
            "Intended Use & Ethical Boundaries",
            "Training, Validation & Evaluation Data",
            "Quantitative Evaluation Benchmarks",
            "Fairness & Sub-Group Disparity Analysis",
            "Explainability & Human-in-the-Loop Safeguards",
            "Model Governance & Maintenance Plan",
        ]

        for section in required_sections:
            assert section in content, f"Missing required section: '{section}' in Model Card"

    def test_ethical_and_non_accusatory_commitments(self):
        content = DOCS_MODEL_CARD.read_text(encoding="utf-8")

        assert "No Accusatory Labeling" in content
        assert "No Arbitrary Blacklisting" in content
        assert "Zero post-fulfillment signals" in content

    def test_fairness_segment_parity_documented(self):
        content = DOCS_MODEL_CARD.read_text(encoding="utf-8")

        for segment in ["new", "regular", "premium", "vip"]:
            assert f"`{segment}`" in content, f"Segment '{segment}' missing from fairness table"
