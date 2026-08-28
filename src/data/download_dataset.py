"""
ReturnGuard AI — Dataset Download Script

Since no suitable public dataset was identified, this script
wraps the synthetic dataset generator as the reproducible
data acquisition process.

Usage:
    python src/data/download_dataset.py

Output:
    data/raw/ecommerce_orders.csv
"""

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "ecommerce_orders.csv"


def main() -> None:
    """Download (generate) the dataset."""
    logger.info("=" * 60)
    logger.info("ReturnGuard AI — Dataset Acquisition")
    logger.info("=" * 60)
    logger.info("")
    logger.info("NOTE: No suitable public dataset with per-order return")
    logger.info("targets and rich pre-fulfillment features was identified.")
    logger.info("Generating synthetic dataset instead.")
    logger.info("")
    logger.info("See docs/dataset-selection.md for evaluation details.")
    logger.info("")

    if OUTPUT_FILE.exists():
        file_size = OUTPUT_FILE.stat().st_size / 1e6
        logger.info("Dataset already exists at %s (%.2f MB)", OUTPUT_FILE, file_size)
        logger.info("To regenerate, delete the file and run again.")
        return

    # Import and run generator
    from src.data.generate_dataset import main as generate_main
    generate_main()

    # Verify
    if OUTPUT_FILE.exists():
        import pandas as pd
        df = pd.read_csv(OUTPUT_FILE)
        logger.info("")
        logger.info("Verification:")
        logger.info("  File exists: True")
        logger.info("  Rows: %d", len(df))
        logger.info("  Columns: %d", len(df.columns))
        logger.info("  Size: %.2f MB", OUTPUT_FILE.stat().st_size / 1e6)
    else:
        logger.error("FAILED: Dataset was not created.")
        sys.exit(1)


if __name__ == "__main__":
    main()
