"""
ReturnGuard AI — Synthetic Dataset Generator

Generates a synthetic e-commerce orders dataset for return-risk prediction.

IMPORTANT: This dataset is synthetically generated for demonstration and
research purposes. It does NOT represent actual merchant or customer data.

Usage:
    python src/data/generate_dataset.py

Output:
    data/raw/ecommerce_orders.csv
"""

import hashlib
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import MLConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ============================================================
# Configuration
# ============================================================

RANDOM_SEED = MLConfig().random_seed
NUM_ORDERS = 100_000
NUM_CUSTOMERS = 10_000
NUM_PRODUCTS = 50
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = OUTPUT_DIR / "ecommerce_orders.csv"

PRODUCT_CATEGORIES = [
    "Electronics",
    "Clothing",
    "Footwear",
    "Beauty",
    "Home",
    "Books",
    "Sports",
    "Accessories",
]

PAYMENT_METHODS = [
    "COD",
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
    "Wallet",
]

CUSTOMER_SEGMENTS = ["new", "regular", "premium", "vip"]

# Category-level base return rates (realistic e-commerce patterns)
CATEGORY_RETURN_RATES = {
    "Electronics": 0.12,
    "Clothing": 0.30,
    "Footwear": 0.28,
    "Beauty": 0.10,
    "Home": 0.15,
    "Books": 0.05,
    "Sports": 0.18,
    "Accessories": 0.20,
}

# Payment method return-rate multipliers
PAYMENT_RETURN_MULTIPLIER = {
    "COD": 1.4,
    "UPI": 0.9,
    "Credit Card": 0.85,
    "Debit Card": 0.95,
    "Net Banking": 0.90,
    "Wallet": 0.88,
}


# ============================================================
# Generator Functions
# ============================================================


def generate_products(rng: np.random.Generator) -> pd.DataFrame:
    """Generate the product catalog."""
    logger.info("Generating %d products...", NUM_PRODUCTS)

    categories = rng.choice(PRODUCT_CATEGORIES, size=NUM_PRODUCTS)

    # Price ranges by category
    price_ranges = {
        "Electronics": (1999, 49999),
        "Clothing": (499, 4999),
        "Footwear": (799, 7999),
        "Beauty": (199, 2999),
        "Home": (999, 14999),
        "Books": (199, 1499),
        "Sports": (599, 9999),
        "Accessories": (299, 3999),
    }

    prices = []
    weights = []
    return_rates = []
    ratings = []

    for cat in categories:
        low, high = price_ranges[cat]
        prices.append(round(rng.uniform(low, high), 0))
        weights.append(int(rng.uniform(50, 15000)))

        # Product-level return rate: category base ± noise
        base_rate = CATEGORY_RETURN_RATES[cat]
        rate = np.clip(rng.normal(base_rate, 0.05), 0.02, 0.55)
        return_rates.append(round(rate, 3))

        ratings.append(round(np.clip(rng.normal(3.8, 0.8), 1.0, 5.0), 1))

    products = pd.DataFrame(
        {
            "product_id": [f"PROD-{i+1:03d}" for i in range(NUM_PRODUCTS)],
            "product_category": categories,
            "product_price": prices,
            "product_weight_grams": weights,
            "product_return_rate": return_rates,
            "product_avg_rating": ratings,
        }
    )

    return products


def generate_customers(rng: np.random.Generator) -> pd.DataFrame:
    """Generate the customer base."""
    logger.info("Generating %d customers...", NUM_CUSTOMERS)

    # Account age: newer customers more common
    account_ages = rng.exponential(scale=365, size=NUM_CUSTOMERS).astype(int)
    account_ages = np.clip(account_ages, 1, 1825)

    # Total orders: follows a power-law-like distribution
    total_orders = (rng.pareto(a=1.5, size=NUM_CUSTOMERS) * 5 + 1).astype(int)
    total_orders = np.clip(total_orders, 1, 100)

    # Customer return rates: most customers are low, some are high
    customer_return_propensity = np.clip(
        rng.beta(a=2, b=5, size=NUM_CUSTOMERS), 0.0, 0.8
    )
    total_returns = (total_orders * customer_return_propensity).astype(int)
    total_returns = np.minimum(total_returns, total_orders)
    return_rates = np.where(
        total_orders > 0, total_returns / total_orders, 0.0
    )

    # Average order value
    avg_order_values = np.clip(
        rng.lognormal(mean=7.5, sigma=0.7, size=NUM_CUSTOMERS), 200, 20000
    ).round(0)

    # Customer segment based on order history
    segments = []
    for orders, age in zip(total_orders, account_ages):
        if orders <= 2 and age < 90:
            segments.append("new")
        elif orders <= 10:
            segments.append("regular")
        elif orders <= 30:
            segments.append("premium")
        else:
            segments.append("vip")

    # Days since last order
    days_since_last = rng.exponential(scale=30, size=NUM_CUSTOMERS).astype(int)
    days_since_last = np.clip(days_since_last, 0, 365)

    customers = pd.DataFrame(
        {
            "customer_id": [f"CUST-{i+1:05d}" for i in range(NUM_CUSTOMERS)],
            "customer_account_age_days": account_ages,
            "customer_total_orders": total_orders,
            "customer_total_returns": total_returns,
            "customer_return_rate": return_rates.round(4),
            "customer_avg_order_value": avg_order_values,
            "customer_segment": segments,
            "customer_days_since_last_order": days_since_last,
        }
    )

    return customers


def generate_orders(
    rng: np.random.Generator,
    customers: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    """Generate orders with realistic return patterns."""
    logger.info("Generating %d orders...", NUM_ORDERS)

    # Assign customers and products to orders
    # Higher-order customers appear more frequently
    customer_weights = customers["customer_total_orders"].values.astype(float)
    customer_weights /= customer_weights.sum()
    customer_indices = rng.choice(
        len(customers), size=NUM_ORDERS, p=customer_weights
    )

    product_indices = rng.choice(len(products), size=NUM_ORDERS)

    # Order dates: uniform across 2 years
    start_date = pd.Timestamp("2024-01-01")
    end_date = pd.Timestamp("2025-12-31")
    total_seconds = int((end_date - start_date).total_seconds())
    random_seconds = rng.integers(0, total_seconds, size=NUM_ORDERS)
    order_dates = start_date + pd.to_timedelta(random_seconds, unit="s")

    # Quantity: most orders are 1-2 items
    quantities = rng.choice([1, 1, 1, 1, 2, 2, 3, 4, 5], size=NUM_ORDERS)

    # Discount: most orders have low/no discount, some have high
    discount_pcts = np.clip(
        rng.exponential(scale=8, size=NUM_ORDERS), 0, 50
    ).round(1)

    # Payment method: weighted distribution
    payment_probs = [0.25, 0.30, 0.15, 0.12, 0.10, 0.08]
    payment_methods = rng.choice(PAYMENT_METHODS, size=NUM_ORDERS, p=payment_probs)

    # Build order-level data
    order_customer_ids = customers.iloc[customer_indices]["customer_id"].values
    order_product_ids = products.iloc[product_indices]["product_id"].values

    # Customer features for each order
    cust_return_rates = customers.iloc[customer_indices]["customer_return_rate"].values
    cust_avg_ovs = customers.iloc[customer_indices]["customer_avg_order_value"].values
    cust_total_orders = customers.iloc[customer_indices]["customer_total_orders"].values
    cust_total_returns = customers.iloc[customer_indices]["customer_total_returns"].values
    cust_account_ages = customers.iloc[customer_indices]["customer_account_age_days"].values
    cust_segments = customers.iloc[customer_indices]["customer_segment"].values
    cust_days_since = customers.iloc[customer_indices]["customer_days_since_last_order"].values

    # Product features for each order
    prod_categories = products.iloc[product_indices]["product_category"].values
    prod_prices = products.iloc[product_indices]["product_price"].values
    prod_weights = products.iloc[product_indices]["product_weight_grams"].values
    prod_return_rates = products.iloc[product_indices]["product_return_rate"].values
    prod_ratings = products.iloc[product_indices]["product_avg_rating"].values

    # Calculated features
    order_values = (prod_prices * quantities * (1 - discount_pcts / 100)).round(0)
    order_value_deviation = np.where(
        cust_avg_ovs > 0, order_values / cust_avg_ovs, 1.0
    ).round(3)
    is_first_order = (cust_total_orders <= 1).astype(int)

    order_hours = order_dates.hour
    order_dow = order_dates.dayofweek
    is_weekend = (order_dow >= 5).astype(int)

    # ============================================================
    # Generate return probability using a logistic model
    # ============================================================
    logger.info("Computing return probabilities...")

    # Build risk score from weighted factors
    risk_score = (
        1.8 * cust_return_rates                              # Customer history
        + 1.2 * prod_return_rates                             # Product history
        + 0.4 * np.clip(order_value_deviation - 1, 0, 5)     # Unusual order value
        + 0.3 * (payment_methods == "COD").astype(float)      # COD risk
        + 0.2 * np.clip(discount_pcts / 50, 0, 1)            # High discount
        + 0.25 * is_first_order                               # First order risk
        + 0.15 * (cust_days_since < 7).astype(float)          # Very recent order
        - 0.3 * np.clip(prod_ratings / 5, 0, 1)              # Good rating reduces risk
        - 0.2 * (cust_segments == "vip").astype(float)        # VIP lower risk
        + rng.normal(0, 0.3, size=NUM_ORDERS)                 # Random noise
    )

    # Convert to probability via sigmoid
    # Offset tuned so overall return rate is ~22% (realistic for e-commerce)
    return_probability = 1 / (1 + np.exp(-(risk_score - 2.6)))

    # Sample binary target from Bernoulli
    is_returned = rng.binomial(1, return_probability)

    # ============================================================
    # Assemble DataFrame
    # ============================================================
    orders = pd.DataFrame(
        {
            # IDs
            "order_id": [f"ORD-{i+1:06d}" for i in range(NUM_ORDERS)],
            "customer_id": order_customer_ids,
            "product_id": order_product_ids,
            # Order features
            "order_date": order_dates,
            "order_value": order_values,
            "quantity": quantities,
            "discount_pct": discount_pcts,
            "payment_method": payment_methods,
            "is_first_order": is_first_order,
            # Customer features
            "customer_account_age_days": cust_account_ages,
            "customer_total_orders": cust_total_orders,
            "customer_total_returns": cust_total_returns,
            "customer_return_rate": cust_return_rates.round(4),
            "customer_avg_order_value": cust_avg_ovs,
            "customer_segment": cust_segments,
            "customer_days_since_last_order": cust_days_since,
            # Product features
            "product_category": prod_categories,
            "product_price": prod_prices,
            "product_weight_grams": prod_weights,
            "product_return_rate": prod_return_rates,
            "product_avg_rating": prod_ratings,
            # Behavioral features
            "order_value_deviation": order_value_deviation,
            "order_hour": order_hours,
            "order_day_of_week": order_dow,
            "is_weekend_order": is_weekend,
            # Target
            "is_returned": is_returned,
        }
    )

    return orders


def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def main() -> None:
    """Generate the synthetic dataset."""
    logger.info("=" * 60)
    logger.info("ReturnGuard AI — Synthetic Dataset Generator")
    logger.info("=" * 60)

    # Check if dataset already exists
    if OUTPUT_FILE.exists():
        logger.info("Dataset already exists at %s", OUTPUT_FILE)
        logger.info("File size: %.2f MB", OUTPUT_FILE.stat().st_size / 1e6)
        existing_df = pd.read_csv(OUTPUT_FILE)
        logger.info("Shape: %s", existing_df.shape)
        logger.info("To regenerate, delete the file and run again.")
        return

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize RNG
    rng = np.random.default_rng(RANDOM_SEED)
    logger.info("Random seed: %d", RANDOM_SEED)

    # Generate components
    products = generate_products(rng)
    customers = generate_customers(rng)
    orders = generate_orders(rng, customers, products)

    # Sort by date
    orders = orders.sort_values("order_date").reset_index(drop=True)

    # Save
    orders.to_csv(OUTPUT_FILE, index=False)
    logger.info("Dataset saved to %s", OUTPUT_FILE)

    # Report
    file_size_mb = OUTPUT_FILE.stat().st_size / 1e6
    sha256_hash = compute_sha256(OUTPUT_FILE)

    logger.info("=" * 60)
    logger.info("DATASET SUMMARY")
    logger.info("=" * 60)
    logger.info("File: %s", OUTPUT_FILE)
    logger.info("Size: %.2f MB", file_size_mb)
    logger.info("Shape: %s", orders.shape)
    logger.info("Columns: %d", len(orders.columns))
    logger.info("SHA-256: %s", sha256_hash)
    logger.info("")
    logger.info("Target distribution:")
    target_counts = orders["is_returned"].value_counts()
    for val, count in target_counts.items():
        pct = count / len(orders) * 100
        label = "Returned" if val == 1 else "Not Returned"
        logger.info("  %s (%d): %d (%.1f%%)", label, val, count, pct)
    logger.info("")
    logger.info("Column list:")
    for col in orders.columns:
        logger.info("  - %s (%s)", col, orders[col].dtype)
    logger.info("=" * 60)
    logger.info("Dataset generation complete.")
    logger.info(
        "NOTE: This dataset is synthetically generated for demonstration "
        "and research purposes."
    )


if __name__ == "__main__":
    main()
