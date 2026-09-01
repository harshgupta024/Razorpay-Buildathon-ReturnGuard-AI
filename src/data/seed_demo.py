"""
ReturnGuard AI — Phase 20: Demo Scenario Seeder & Pre-packaged Scenarios

Seeds the database with representative real-time scored orders and pending review items:
1. Low Risk orders (Safe VIP, Regular repeat purchases)
2. Medium Risk orders (Borderline apparel, sizing verification)
3. High & Critical Risk orders (Pending in the Human Review Queue)
4. Saves pre-configured judge demo scenarios to data/demo_scenarios.json

Usage:
    python src/data/seed_demo.py --count 200
"""

import argparse
import json
import logging
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.business.cost_engine import BusinessCostEngine, OrderFinancialProfile
from src.db.session import (
    AuditLogRecord,
    OrderRecord,
    ReviewRecord,
    RiskAssessmentRecord,
    SessionLocal,
    init_db,
)
from src.explainability.explainer import RiskExplainer
from src.risk.scoring_engine import RiskScoringEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("returnguard.seed_demo")

DEMO_SCENARIOS_PATH = PROJECT_ROOT / "data" / "demo_scenarios.json"
VAL_SPLIT_PATH = PROJECT_ROOT / "data" / "splits" / "val.csv"


CURATED_DEMO_SCENARIOS = [
    {
        "scenario_id": "SCENARIO-1-SAFE-VIP",
        "scenario_name": "🟢 VIP Customer — Frictionless 1-Click Buy",
        "story": "Loyal customer (400+ days tenure, 12 prior orders, 1 return) buying Books via Prepaid UPI. Low risk, instant fulfillment.",
        "order": {
            "order_id": "ORD-VIP-0091",
            "customer_id": "CUST-VIP-042",
            "product_id": "PROD-BOOK-12",
            "order_value": 1850.0,
            "product_category": "Books",
            "payment_method": "UPI",
            "quantity": 2,
            "discount_pct": 10.0,
            "customer_account_age_days": 420,
            "customer_total_orders": 12,
            "customer_total_returns": 1,
            "customer_return_rate": 0.083,
            "product_price": 925.0,
            "product_weight_grams": 750.0,
            "product_return_rate": 0.095,
            "product_avg_rating": 4.8,
            "order_value_deviation": 0.95,
            "customer_segment": "vip",
            "is_first_order": 0,
        },
    },
    {
        "scenario_id": "SCENARIO-2-BORDERLINE-COD",
        "scenario_name": "🟡 Borderline Fashion — Interactive WhatsApp Verify",
        "story": "Regular customer ordering Rs. 3,600 Clothing on COD with heavy discount (30%). Soft verification protects Rs. 140 net.",
        "order": {
            "order_id": "ORD-MED-4421",
            "customer_id": "CUST-REG-204",
            "product_id": "PROD-DRESS-88",
            "order_value": 3600.0,
            "product_category": "Clothing",
            "payment_method": "COD",
            "quantity": 1,
            "discount_pct": 30.0,
            "customer_account_age_days": 95,
            "customer_total_orders": 4,
            "customer_total_returns": 1,
            "customer_return_rate": 0.25,
            "product_price": 3600.0,
            "product_weight_grams": 600.0,
            "product_return_rate": 0.31,
            "product_avg_rating": 4.1,
            "order_value_deviation": 1.45,
            "customer_segment": "regular",
            "is_first_order": 0,
        },
    },
    {
        "scenario_id": "SCENARIO-3-REPEAT-RETURNER-COD",
        "scenario_name": "🟠 High Risk Footwear — Require Rs. 100 Shipping Deposit",
        "story": "Customer with 60% historical return rate buying Rs. 8,900 shoes on COD (3.2x typical cart size). Requires Rs. 100 deposit to avoid loss.",
        "order": {
            "order_id": "ORD-HIGH-8812",
            "customer_id": "CUST-RISK-990",
            "product_id": "PROD-SHOE-31",
            "order_value": 8900.0,
            "product_category": "Footwear",
            "payment_method": "COD",
            "quantity": 3,
            "discount_pct": 40.0,
            "customer_account_age_days": 35,
            "customer_total_orders": 5,
            "customer_total_returns": 3,
            "customer_return_rate": 0.60,
            "product_price": 2966.0,
            "product_weight_grams": 2400.0,
            "product_return_rate": 0.38,
            "product_avg_rating": 3.5,
            "order_value_deviation": 3.20,
            "customer_segment": "new",
            "is_first_order": 0,
        },
    },
    {
        "scenario_id": "SCENARIO-4-HIGH-VALUE-CRITICAL",
        "scenario_name": "🔴 Critical Risk Electronics — Merchant Review Queue",
        "story": "New account (3 days old) ordering Rs. 14,500 Electronics on COD (4.0x basket deviation). Routed to manual support review queue.",
        "order": {
            "order_id": "ORD-CRIT-9921",
            "customer_id": "CUST-NEW-019",
            "product_id": "PROD-ELEC-55",
            "order_value": 14500.0,
            "product_category": "Electronics",
            "payment_method": "COD",
            "quantity": 1,
            "discount_pct": 20.0,
            "customer_account_age_days": 3,
            "customer_total_orders": 1,
            "customer_total_returns": 0,
            "customer_return_rate": 0.0,
            "product_price": 14500.0,
            "product_weight_grams": 1800.0,
            "product_return_rate": 0.22,
            "product_avg_rating": 3.8,
            "order_value_deviation": 4.10,
            "customer_segment": "new",
            "is_first_order": 1,
        },
    },
]


def seed_demo_database(num_records: int = 200) -> None:
    """Seed relational database with scored orders and review queue items."""
    init_db()
    db = SessionLocal()

    # Save Curated Scenarios JSON
    with open(DEMO_SCENARIOS_PATH, "w", encoding="utf-8") as f:
        json.dump(CURATED_DEMO_SCENARIOS, f, indent=2)
    logger.info(f"Saved curated demo scenarios to {DEMO_SCENARIOS_PATH}")

    scoring_engine = RiskScoringEngine()
    explainer = RiskExplainer()

    # 1. Seed Curated Scenarios First
    logger.info("Seeding primary curated demo scenarios...")
    for sc in CURATED_DEMO_SCENARIOS:
        order_dict = sc["order"]
        score_res = scoring_engine.score_order(order_dict)
        explanation = explainer.explain_order(order_dict)

        existing = db.query(OrderRecord).filter_by(order_id=order_dict["order_id"]).first()
        if not existing:
            order_rec = OrderRecord(
                order_id=order_dict["order_id"],
                customer_id=order_dict["customer_id"],
                product_id=order_dict["product_id"],
                order_value=order_dict["order_value"],
                product_category=order_dict["product_category"],
                payment_method=order_dict["payment_method"],
                quantity=order_dict.get("quantity", 1),
                discount_pct=order_dict.get("discount_pct", 0.0),
                customer_account_age_days=order_dict.get("customer_account_age_days", 30),
                customer_total_orders=order_dict.get("customer_total_orders", 1),
                customer_total_returns=order_dict.get("customer_total_returns", 0),
                customer_return_rate=order_dict.get("customer_return_rate", 0.0),
                product_price=order_dict.get("product_price", order_dict["order_value"]),
                product_weight_grams=order_dict.get("product_weight_grams", 1000.0),
                product_return_rate=order_dict.get("product_return_rate", 0.20),
                order_value_deviation=order_dict.get("order_value_deviation", 1.0),
                is_first_order=order_dict.get("is_first_order", 0),
                created_at=datetime.utcnow() - timedelta(minutes=np.random.randint(5, 120)),
            )
            db.add(order_rec)

            assessment_rec = RiskAssessmentRecord(
                order_id=order_dict["order_id"],
                predicted_return_probability=score_res.predicted_return_probability,
                risk_score=score_res.risk_score,
                risk_tier=score_res.risk_tier.value,
                gross_return_loss_inr=score_res.gross_return_loss_inr,
                unmitigated_expected_loss_inr=score_res.unmitigated_expected_loss_inr,
                recommended_action=score_res.recommended_action.value,
                recommended_action_name=score_res.recommended_action_name,
                expected_net_savings_inr=score_res.expected_net_savings_inr,
                mitigated_expected_loss_inr=score_res.mitigated_expected_loss_inr,
                action_rationale=score_res.action_rationale,
                top_risk_factors=[rf.__dict__ for rf in explanation.top_risk_factors],
                top_protective_factors=[pf.__dict__ for pf in explanation.top_protective_factors],
                plain_language_summary=explanation.plain_language_summary,
                latency_ms=score_res.latency_ms,
            )
            db.add(assessment_rec)

    # 2. Seed Batch from Validation Split
    if VAL_SPLIT_PATH.exists():
        logger.info(f"Seeding {num_records} background orders from {VAL_SPLIT_PATH}...")
        val_df = pd.read_csv(VAL_SPLIT_PATH).head(num_records)

        for _, row in val_df.iterrows():
            order_dict = row.to_dict()
            order_id = str(order_dict.get("order_id", f"ORD-{uuid.uuid4().hex[:6].upper()}"))

            existing = db.query(OrderRecord).filter_by(order_id=order_id).first()
            if existing:
                continue

            score_res = scoring_engine.score_order(order_dict)
            explanation = explainer.explain_order(order_dict)

            order_rec = OrderRecord(
                order_id=order_id,
                customer_id=str(order_dict.get("customer_id", "CUST-001")),
                product_id=str(order_dict.get("product_id", "PROD-001")),
                order_value=float(order_dict.get("order_value", 2000.0)),
                product_category=str(order_dict.get("product_category", "Clothing")),
                payment_method=str(order_dict.get("payment_method", "UPI")),
                quantity=int(order_dict.get("quantity", 1)),
                discount_pct=float(order_dict.get("discount_pct", 0.0)),
                customer_account_age_days=int(order_dict.get("customer_account_age_days", 30)),
                customer_total_orders=int(order_dict.get("customer_total_orders", 1)),
                customer_total_returns=int(order_dict.get("customer_total_returns", 0)),
                customer_return_rate=float(order_dict.get("customer_return_rate", 0.0)),
                product_price=float(order_dict.get("product_price", 2000.0)),
                product_weight_grams=float(order_dict.get("product_weight_grams", 1000.0)),
                product_return_rate=float(order_dict.get("product_return_rate", 0.20)),
                order_value_deviation=float(order_dict.get("order_value_deviation", 1.0)),
                is_first_order=int(order_dict.get("is_first_order", 0)),
                created_at=datetime.utcnow() - timedelta(minutes=np.random.randint(10, 1440)),
            )
            db.add(order_rec)

            assessment_rec = RiskAssessmentRecord(
                order_id=order_id,
                predicted_return_probability=score_res.predicted_return_probability,
                risk_score=score_res.risk_score,
                risk_tier=score_res.risk_tier.value,
                gross_return_loss_inr=score_res.gross_return_loss_inr,
                unmitigated_expected_loss_inr=score_res.unmitigated_expected_loss_inr,
                recommended_action=score_res.recommended_action.value,
                recommended_action_name=score_res.recommended_action_name,
                expected_net_savings_inr=score_res.expected_net_savings_inr,
                mitigated_expected_loss_inr=score_res.mitigated_expected_loss_inr,
                action_rationale=score_res.action_rationale,
                top_risk_factors=[rf.__dict__ for rf in explanation.top_risk_factors],
                top_protective_factors=[pf.__dict__ for pf in explanation.top_protective_factors],
                plain_language_summary=explanation.plain_language_summary,
                latency_ms=score_res.latency_ms,
            )
            db.add(assessment_rec)

    db.commit()
    db.close()
    logger.info("Demo database seeding complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed demo database for ReturnGuard AI")
    parser.add_argument("--count", type=int, default=150, help="Number of background orders to seed")
    args = parser.parse_args()
    seed_demo_database(args.count)
