"""
ReturnGuard AI — Real-Time Dataset Ingestion & Stream Processing Engine

Ingests genuine historical orders directly from the 100,000 e-commerce dataset,
computes real-time ML risk predictions and financial mitigation assessments,
and persists real records to the database.

Usage:
    python src/data/stream_orders.py --source data/splits/val.csv --batch-size 100
"""

import argparse
import logging
import sys
import time
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.db.session import (
    AuditLogRecord,
    OrderRecord,
    RiskAssessmentRecord,
    SessionLocal,
    init_db,
)
from src.explainability.explainer import RiskExplainer
from src.risk.scoring_engine import RiskScoringEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("returnguard.stream_orders")

DEFAULT_DATASET = PROJECT_ROOT / "data" / "splits" / "val.csv"


def stream_and_score_dataset(
    source_csv: Path = DEFAULT_DATASET,
    limit: int = 500,
    batch_size: int = 50,
) -> None:
    """Stream real orders from the dataset through the calibrated scoring pipeline."""
    init_db()
    db = SessionLocal()

    if not Path(source_csv).exists():
        logger.error(f"Dataset not found at {source_csv}")
        return

    logger.info(f"Loading real dataset from {source_csv}...")
    df = pd.read_csv(source_csv).head(limit)
    total_orders = len(df)
    logger.info(f"Loaded {total_orders:,} genuine order records for real-time processing.")

    scoring_engine = RiskScoringEngine()
    explainer = RiskExplainer()

    start_time = time.perf_counter()
    processed_count = 0

    for idx, row in df.iterrows():
        order_dict = row.to_dict()
        order_id = str(order_dict.get("order_id", f"ORD-{idx:06d}"))

        # Check if already in database
        existing = db.query(OrderRecord).filter_by(order_id=order_id).first()
        if existing:
            continue

        # Real inference & financial loss evaluation
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

        # Audit Event
        audit = AuditLogRecord(
            event_type="REALTIME_ORDER_INGESTED",
            order_id=order_id,
            actor="dataset_streamer",
            payload={
                "risk_tier": score_res.risk_tier.value,
                "predicted_return_probability": score_res.predicted_return_probability,
                "recommended_action": score_res.recommended_action.value,
            },
        )
        db.add(audit)
        processed_count += 1

        if processed_count % batch_size == 0:
            db.commit()
            logger.info(f"Ingested & scored {processed_count:,} / {total_orders:,} orders...")

    db.commit()
    db.close()

    elapsed = time.perf_counter() - start_time
    logger.info(
        f"Completed real-time streaming: {processed_count:,} orders scored in {elapsed:.2f}s "
        f"({processed_count/max(1e-3, elapsed):,.0f} orders/sec)."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest and score real dataset records")
    parser.add_argument("--source", type=str, default=str(DEFAULT_DATASET), help="Path to dataset split CSV")
    parser.add_argument("--limit", type=int, default=300, help="Maximum orders to ingest")
    parser.add_argument("--batch-size", type=int, default=50, help="Commit batch size")
    args = parser.parse_args()

    stream_and_score_dataset(Path(args.source), args.limit, args.batch_size)
