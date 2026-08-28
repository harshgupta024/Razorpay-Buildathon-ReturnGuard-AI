"""
Tests for ReturnGuard AI configuration module.
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    AppConfig,
    BackendConfig,
    CostConfig,
    DatabaseConfig,
    MLConfig,
    RiskConfig,
    load_config_from_env,
    PROJECT_ROOT as CONFIG_PROJECT_ROOT,
)


class TestAppConfig:
    """Test application configuration defaults."""

    def test_default_values(self):
        config = AppConfig()
        assert config.app_name == "ReturnGuard AI"
        assert config.app_env == "development"
        assert config.debug is True
        assert config.log_level == "INFO"


class TestBackendConfig:
    """Test backend configuration defaults."""

    def test_default_values(self):
        config = BackendConfig()
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert "http://localhost:5173" in config.cors_origins
        assert "http://localhost:3000" in config.cors_origins


class TestMLConfig:
    """Test ML configuration defaults."""

    def test_default_values(self):
        config = MLConfig()
        assert config.random_seed == 42
        assert config.model_version == "returnguard-v1"
        assert config.test_size == 0.15
        assert config.val_size == 0.15
        assert config.train_size == 0.70

    def test_split_sizes_sum_to_one(self):
        config = MLConfig()
        total = config.train_size + config.val_size + config.test_size
        assert abs(total - 1.0) < 1e-9, f"Split sizes sum to {total}, expected 1.0"


class TestCostConfig:
    """Test business cost configuration defaults."""

    def test_default_values(self):
        config = CostConfig()
        assert config.avg_order_value == 3000.0
        assert config.avg_margin_pct == 0.30
        assert config.return_shipping_cost == 150.0
        assert config.handling_cost == 100.0
        assert config.restocking_loss_pct == 0.10
        assert config.manual_review_cost == 50.0
        assert config.estimated_conversion_loss == 200.0

    def test_false_negative_more_expensive_than_false_positive(self):
        """FN cost should be significantly higher than FP cost."""
        config = CostConfig()
        fn_cost = (
            config.return_shipping_cost
            + config.handling_cost
            + config.avg_order_value * config.restocking_loss_pct
            + config.avg_order_value * config.avg_margin_pct
        )
        fp_cost = config.manual_review_cost + config.estimated_conversion_loss
        assert fn_cost > fp_cost, (
            f"FN cost (₹{fn_cost}) should exceed FP cost (₹{fp_cost})"
        )


class TestRiskConfig:
    """Test risk threshold configuration."""

    def test_default_values(self):
        config = RiskConfig()
        assert config.threshold_low == 0.30
        assert config.threshold_high == 0.70

    def test_threshold_ordering(self):
        config = RiskConfig()
        assert config.threshold_low < config.threshold_high

    def test_thresholds_in_valid_range(self):
        config = RiskConfig()
        assert 0.0 < config.threshold_low < 1.0
        assert 0.0 < config.threshold_high < 1.0


class TestLoadConfig:
    """Test configuration loading from environment."""

    def test_load_config_returns_all_sections(self):
        config = load_config_from_env()
        assert "app" in config
        assert "backend" in config
        assert "database" in config
        assert "ml" in config
        assert "cost" in config
        assert "risk" in config

    def test_env_override(self):
        """Environment variables should override defaults."""
        os.environ["RANDOM_SEED"] = "123"
        try:
            config = load_config_from_env()
            assert config["ml"].random_seed == 123
        finally:
            os.environ.pop("RANDOM_SEED", None)


class TestProjectRoot:
    """Test project root detection."""

    def test_project_root_exists(self):
        assert CONFIG_PROJECT_ROOT.exists()

    def test_project_root_contains_src(self):
        assert (CONFIG_PROJECT_ROOT / "src").exists()
