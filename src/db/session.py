"""
ReturnGuard AI — Database Layer: SQLAlchemy Models & Session Management

Provides relational storage for:
1. Orders and customer metadata
2. ML Risk Assessments & Financial Evaluations
3. Human-in-the-loop review queue decisions
4. Immutable audit event logs
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "returnguard.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

logger = logging.getLogger(__name__)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite concurrency with FastAPI
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class OrderRecord(Base):
    """Stores incoming e-commerce order metadata."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), unique=True, index=True, nullable=False)
    customer_id = Column(String(64), index=True, nullable=False)
    product_id = Column(String(64), index=True, nullable=False)
    order_value = Column(Float, nullable=False)
    product_category = Column(String(64), nullable=False)
    payment_method = Column(String(32), nullable=False)
    quantity = Column(Integer, default=1)
    discount_pct = Column(Float, default=0.0)
    customer_account_age_days = Column(Integer, default=30)
    customer_total_orders = Column(Integer, default=1)
    customer_total_returns = Column(Integer, default=0)
    customer_return_rate = Column(Float, default=0.0)
    product_price = Column(Float, default=1000.0)
    product_weight_grams = Column(Float, default=1000.0)
    product_return_rate = Column(Float, default=0.20)
    order_value_deviation = Column(Float, default=1.0)
    is_first_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    assessment = relationship("RiskAssessmentRecord", back_populates="order", uselist=False, cascade="all, delete-orphan")
    review = relationship("ReviewRecord", back_populates="order", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLogRecord", back_populates="order", cascade="all, delete-orphan")


class RiskAssessmentRecord(Base):
    """Stores ML risk score, financial loss evaluation, and recommended policy."""
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), ForeignKey("orders.order_id"), unique=True, index=True, nullable=False)
    predicted_return_probability = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_tier = Column(String(32), nullable=False, index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    gross_return_loss_inr = Column(Float, nullable=False)
    unmitigated_expected_loss_inr = Column(Float, nullable=False)
    recommended_action = Column(String(64), nullable=False)
    recommended_action_name = Column(String(128), nullable=False)
    expected_net_savings_inr = Column(Float, nullable=False)
    mitigated_expected_loss_inr = Column(Float, nullable=False)
    action_rationale = Column(Text, nullable=False)
    top_risk_factors = Column(JSON, default=list)
    top_protective_factors = Column(JSON, default=list)
    plain_language_summary = Column(Text, nullable=True)
    scored_at = Column(DateTime, default=datetime.utcnow, index=True)
    latency_ms = Column(Float, default=0.0)

    # Relationships
    order = relationship("OrderRecord", back_populates="assessment")


class ReviewRecord(Base):
    """Stores human-in-the-loop merchant review decisions and overrides."""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), ForeignKey("orders.order_id"), unique=True, index=True, nullable=False)
    original_risk_tier = Column(String(32), nullable=False)
    original_action = Column(String(64), nullable=False)
    decision = Column(String(64), nullable=False)  # APPROVED_SEAMLESS, REQUIRED_DEPOSIT, REQUIRED_WHATSAPP, CANCELLED
    notes = Column(Text, nullable=True)
    reviewer_id = Column(String(64), default="merchant_admin")
    reviewed_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_overridden = Column(Boolean, default=False)

    # Relationships
    order = relationship("OrderRecord", back_populates="review")


class AuditLogRecord(Base):
    """Immutable audit trail for all system and merchant decision events."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(64), nullable=False, index=True)  # ORDER_SCORED, REVIEW_SUBMITTED, THRESHOLD_UPDATED
    order_id = Column(String(64), ForeignKey("orders.order_id"), nullable=True, index=True)
    actor = Column(String(64), default="system")
    payload = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    order = relationship("OrderRecord", back_populates="audit_logs")


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info(f"Initialized database schema at {DB_PATH}")


def get_db() -> Generator:
    """FastAPI database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
