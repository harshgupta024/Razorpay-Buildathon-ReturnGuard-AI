"""
ReturnGuard AI — Shared Configuration

Central configuration loaded from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class AppConfig:
    """Application-level configuration."""
    app_name: str = "ReturnGuard AI"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"


@dataclass
class BackendConfig:
    """Backend server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = field(default_factory=lambda: [
        "http://localhost:5173",
        "http://localhost:3000",
    ])


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str = f"sqlite:///{PROJECT_ROOT / 'data' / 'returnguard.db'}"


@dataclass
class MLConfig:
    """Machine learning configuration."""
    model_path: Path = field(default_factory=lambda: PROJECT_ROOT / "models")
    random_seed: int = 42
    model_version: str = "returnguard-v1"
    test_size: float = 0.15
    val_size: float = 0.15
    train_size: float = 0.70


@dataclass
class CostConfig:
    """Business cost model configuration.

    IMPORTANT: These are configurable assumptions for demonstration.
    They do NOT represent actual merchant costs.
    """
    avg_order_value: float = 3000.0
    avg_margin_pct: float = 0.30
    return_shipping_cost: float = 150.0
    handling_cost: float = 100.0
    restocking_loss_pct: float = 0.10
    manual_review_cost: float = 50.0
    estimated_conversion_loss: float = 200.0


@dataclass
class RiskConfig:
    """Risk threshold configuration."""
    threshold_low: float = 0.30
    threshold_high: float = 0.70


def load_config_from_env() -> dict:
    """Load all configuration from environment variables with defaults."""
    return {
        "app": AppConfig(
            app_name=os.getenv("APP_NAME", "ReturnGuard AI"),
            app_env=os.getenv("APP_ENV", "development"),
            debug=os.getenv("DEBUG", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        ),
        "backend": BackendConfig(
            host=os.getenv("BACKEND_HOST", "0.0.0.0"),
            port=int(os.getenv("BACKEND_PORT", "8000")),
            cors_origins=os.getenv(
                "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
            ).split(","),
        ),
        "database": DatabaseConfig(
            url=os.getenv(
                "DATABASE_URL",
                f"sqlite:///{PROJECT_ROOT / 'data' / 'returnguard.db'}",
            ),
        ),
        "ml": MLConfig(
            model_path=Path(os.getenv("MODEL_PATH", str(PROJECT_ROOT / "models"))),
            random_seed=int(os.getenv("RANDOM_SEED", "42")),
            model_version=os.getenv("MODEL_VERSION", "returnguard-v1"),
        ),
        "cost": CostConfig(
            avg_order_value=float(os.getenv("AVG_ORDER_VALUE", "3000")),
            avg_margin_pct=float(os.getenv("AVG_MARGIN_PCT", "0.30")),
            return_shipping_cost=float(os.getenv("RETURN_SHIPPING_COST", "150")),
            handling_cost=float(os.getenv("HANDLING_COST", "100")),
            restocking_loss_pct=float(os.getenv("RESTOCKING_LOSS_PCT", "0.10")),
            manual_review_cost=float(os.getenv("MANUAL_REVIEW_COST", "50")),
            estimated_conversion_loss=float(
                os.getenv("ESTIMATED_CONVERSION_LOSS", "200")
            ),
        ),
        "risk": RiskConfig(
            threshold_low=float(os.getenv("RISK_THRESHOLD_LOW", "0.30")),
            threshold_high=float(os.getenv("RISK_THRESHOLD_HIGH", "0.70")),
        ),
    }
