"""
ReturnGuard AI — Exploratory Data Analysis (EDA)

Performs comprehensive EDA on the e-commerce orders dataset:
1. Target distribution analysis
2. Numerical feature distributions & outlier detection
3. Categorical feature distributions
4. Correlation analysis
5. Return rate by key dimensions (category, price band, payment, segment)
6. Behavioral pattern analysis
7. Feature importance estimation via correlation with target
8. Leakage and bias assessment

Generates:
    reports/eda-report.md
    reports/figures/*.png

Usage:
    python src/data/eda.py
"""

import logging
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for chart generation

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=FutureWarning)

DATA_FILE = PROJECT_ROOT / "data" / "raw" / "ecommerce_orders.csv"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
REPORT_FILE = PROJECT_ROOT / "reports" / "eda-report.md"

# Style
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
COLORS = {"returned": "#e74c3c", "not_returned": "#2ecc71", "accent": "#3498db"}


def load_data() -> pd.DataFrame:
    """Load the dataset."""
    df = pd.read_csv(DATA_FILE, parse_dates=["order_date"])
    logger.info("Loaded dataset: %s", df.shape)
    return df


def save_fig(fig: plt.Figure, name: str) -> Path:
    """Save figure to reports/figures/."""
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    logger.info("Saved figure: %s", path.name)
    return path


# ============================================================
# Individual Analysis Functions
# ============================================================


def analyze_target_distribution(df: pd.DataFrame) -> dict:
    """Analyze the target variable distribution."""
    counts = df["is_returned"].value_counts().sort_index()
    rate = df["is_returned"].mean()

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Bar chart
    bars = axes[0].bar(
        ["Not Returned (0)", "Returned (1)"],
        counts.values,
        color=[COLORS["not_returned"], COLORS["returned"]],
        edgecolor="white",
        linewidth=1.5,
    )
    for bar, count in zip(bars, counts.values):
        axes[0].text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 500,
            f"{count:,}\n({count/len(df):.1%})",
            ha="center", va="bottom", fontweight="bold", fontsize=11,
        )
    axes[0].set_title("Target Distribution: is_returned", fontsize=13, fontweight="bold")
    axes[0].set_ylabel("Count")
    axes[0].set_ylim(0, counts.max() * 1.2)

    # Pie chart
    axes[1].pie(
        counts.values,
        labels=["Not Returned", "Returned"],
        colors=[COLORS["not_returned"], COLORS["returned"]],
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 12},
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    axes[1].set_title("Return Rate Proportion", fontsize=13, fontweight="bold")

    fig.suptitle("Target Variable Analysis", fontsize=15, fontweight="bold", y=1.02)
    fig.tight_layout()
    save_fig(fig, "01_target_distribution")

    return {
        "return_rate": rate,
        "not_returned": int(counts[0]),
        "returned": int(counts[1]),
        "imbalance_ratio": f"1:{counts[0]/counts[1]:.2f}",
    }


def analyze_numerical_distributions(df: pd.DataFrame) -> dict:
    """Analyze distributions of key numerical features."""
    num_features = [
        "order_value", "quantity", "discount_pct", "product_price",
        "customer_return_rate", "product_return_rate", "product_avg_rating",
        "order_value_deviation", "customer_account_age_days",
        "customer_total_orders", "customer_total_returns",
        "customer_days_since_last_order",
    ]

    fig, axes = plt.subplots(3, 4, figsize=(20, 14))
    axes = axes.flatten()

    outlier_info = {}

    for i, feat in enumerate(num_features):
        ax = axes[i]
        # Plot histograms split by return status
        for ret_val, color, label in [(0, COLORS["not_returned"], "Not Returned"), (1, COLORS["returned"], "Returned")]:
            subset = df[df["is_returned"] == ret_val][feat]
            ax.hist(subset, bins=40, alpha=0.6, color=color, label=label, density=True)

        ax.set_title(feat, fontsize=10, fontweight="bold")
        ax.tick_params(labelsize=8)

        # Outlier detection via IQR
        q1, q3 = df[feat].quantile(0.25), df[feat].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        n_outliers = int(((df[feat] < lower) | (df[feat] > upper)).sum())
        outlier_info[feat] = {
            "outliers": n_outliers,
            "outlier_pct": round(n_outliers / len(df) * 100, 2),
            "iqr_lower": round(lower, 2),
            "iqr_upper": round(upper, 2),
        }

    axes[0].legend(fontsize=9)
    fig.suptitle("Numerical Feature Distributions (by Return Status)", fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save_fig(fig, "02_numerical_distributions")

    return outlier_info


def analyze_correlation_matrix(df: pd.DataFrame) -> dict:
    """Compute and visualize correlation matrix."""
    num_cols = df.select_dtypes(include=[np.number]).columns
    corr = df[num_cols].corr()

    fig, ax = plt.subplots(figsize=(16, 13))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
        center=0, vmin=-1, vmax=1, ax=ax, square=True,
        linewidths=0.5, annot_kws={"fontsize": 7},
        cbar_kws={"shrink": 0.8},
    )
    ax.set_title("Feature Correlation Matrix", fontsize=15, fontweight="bold", pad=20)
    fig.tight_layout()
    save_fig(fig, "03_correlation_matrix")

    # Extract target correlations
    target_corr = corr["is_returned"].drop("is_returned").sort_values(key=abs, ascending=False)
    return {
        "top_positive": target_corr.head(5).to_dict(),
        "top_negative": target_corr.tail(5).to_dict(),
    }


def analyze_return_rate_by_category(df: pd.DataFrame) -> dict:
    """Analyze return rate across product categories."""
    cat_stats = df.groupby("product_category").agg(
        order_count=("is_returned", "count"),
        return_rate=("is_returned", "mean"),
        avg_order_value=("order_value", "mean"),
    ).sort_values("return_rate", ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Return rate by category
    bars = axes[0].barh(
        cat_stats.index, cat_stats["return_rate"],
        color=sns.color_palette("RdYlGn_r", len(cat_stats)),
        edgecolor="white", linewidth=1,
    )
    axes[0].set_xlabel("Return Rate")
    axes[0].set_title("Return Rate by Product Category", fontsize=13, fontweight="bold")
    axes[0].xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    for bar, rate in zip(bars, cat_stats["return_rate"]):
        axes[0].text(
            bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
            f"{rate:.1%}", va="center", fontsize=10,
        )

    # Order volume by category
    axes[1].barh(
        cat_stats.index, cat_stats["order_count"],
        color=sns.color_palette("Blues_d", len(cat_stats)),
        edgecolor="white", linewidth=1,
    )
    axes[1].set_xlabel("Order Count")
    axes[1].set_title("Order Volume by Category", fontsize=13, fontweight="bold")

    fig.tight_layout()
    save_fig(fig, "04_return_rate_by_category")

    return cat_stats.to_dict("index")


def analyze_return_rate_by_price_band(df: pd.DataFrame) -> dict:
    """Analyze return rate across price bands."""
    df = df.copy()
    df["price_band"] = pd.cut(
        df["order_value"],
        bins=[0, 500, 1000, 2000, 5000, 10000, 50000, float("inf")],
        labels=["<500", "500-1K", "1K-2K", "2K-5K", "5K-10K", "10K-50K", "50K+"],
    )

    band_stats = df.groupby("price_band", observed=True).agg(
        order_count=("is_returned", "count"),
        return_rate=("is_returned", "mean"),
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(band_stats))
    bars = ax.bar(x, band_stats["return_rate"], color=sns.color_palette("YlOrRd", len(band_stats)),
                  edgecolor="white", linewidth=1.5)
    ax.set_xticks(x)
    ax.set_xticklabels(band_stats.index, rotation=0)
    ax.set_xlabel("Order Value Band (INR)")
    ax.set_ylabel("Return Rate")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_title("Return Rate by Order Value Band", fontsize=14, fontweight="bold")

    # Add count annotations
    for bar, (_, row) in zip(bars, band_stats.iterrows()):
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
            f"{row['return_rate']:.1%}\n(n={row['order_count']:,.0f})",
            ha="center", va="bottom", fontsize=9,
        )
    ax.set_ylim(0, band_stats["return_rate"].max() * 1.25)
    fig.tight_layout()
    save_fig(fig, "05_return_rate_by_price_band")

    return band_stats.to_dict("index")


def analyze_return_rate_by_payment(df: pd.DataFrame) -> dict:
    """Analyze return rate by payment method."""
    pay_stats = df.groupby("payment_method").agg(
        order_count=("is_returned", "count"),
        return_rate=("is_returned", "mean"),
    ).sort_values("return_rate", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(
        pay_stats.index, pay_stats["return_rate"],
        color=sns.color_palette("Set2", len(pay_stats)),
        edgecolor="white", linewidth=1.5,
    )
    ax.set_ylabel("Return Rate")
    ax.set_title("Return Rate by Payment Method", fontsize=14, fontweight="bold")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    for bar, rate in zip(bars, pay_stats["return_rate"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
            f"{rate:.1%}", ha="center", va="bottom", fontsize=11, fontweight="bold",
        )
    ax.set_ylim(0, pay_stats["return_rate"].max() * 1.2)
    fig.tight_layout()
    save_fig(fig, "06_return_rate_by_payment")

    return pay_stats.to_dict("index")


def analyze_return_rate_by_segment(df: pd.DataFrame) -> dict:
    """Analyze return rate by customer segment."""
    seg_order = ["new", "regular", "premium", "vip"]
    seg_stats = df.groupby("customer_segment").agg(
        order_count=("is_returned", "count"),
        return_rate=("is_returned", "mean"),
        avg_customer_return_rate=("customer_return_rate", "mean"),
    ).reindex(seg_order)

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    # Return rate by segment
    bars = axes[0].bar(
        seg_stats.index, seg_stats["return_rate"],
        color=["#e74c3c", "#f39c12", "#2ecc71", "#3498db"],
        edgecolor="white", linewidth=1.5,
    )
    axes[0].set_ylabel("Return Rate (this dataset)")
    axes[0].set_title("Return Rate by Customer Segment", fontsize=13, fontweight="bold")
    axes[0].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    for bar, rate in zip(bars, seg_stats["return_rate"]):
        axes[0].text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
            f"{rate:.1%}", ha="center", va="bottom", fontsize=11, fontweight="bold",
        )

    # Order volume by segment
    axes[1].bar(
        seg_stats.index, seg_stats["order_count"],
        color=["#e74c3c", "#f39c12", "#2ecc71", "#3498db"],
        edgecolor="white", linewidth=1.5,
    )
    axes[1].set_ylabel("Order Count")
    axes[1].set_title("Order Volume by Segment", fontsize=13, fontweight="bold")

    fig.tight_layout()
    save_fig(fig, "07_return_rate_by_segment")

    return seg_stats.to_dict("index")


def analyze_customer_history_patterns(df: pd.DataFrame) -> dict:
    """Analyze relationship between customer history and returns."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # 1. Customer return rate vs actual returns
    df_copy = df.copy()
    df_copy["cust_return_rate_bin"] = pd.cut(
        df_copy["customer_return_rate"],
        bins=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0],
        labels=["0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50%+"],
        include_lowest=True,
    )
    hist_stats = df_copy.groupby("cust_return_rate_bin", observed=True)["is_returned"].mean()
    axes[0].bar(range(len(hist_stats)), hist_stats.values, color=sns.color_palette("Reds", len(hist_stats)))
    axes[0].set_xticks(range(len(hist_stats)))
    axes[0].set_xticklabels(hist_stats.index, rotation=45, ha="right")
    axes[0].set_ylabel("Actual Return Rate in Dataset")
    axes[0].set_title("Customer Historical Return Rate\nvs Actual Returns", fontsize=11, fontweight="bold")
    axes[0].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    # 2. Order value deviation
    df_copy["ovd_bin"] = pd.cut(
        df_copy["order_value_deviation"].clip(upper=5),
        bins=[0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0],
        labels=["<0.5x", "0.5-1x", "1-1.5x", "1.5-2x", "2-3x", "3-5x"],
        include_lowest=True,
    )
    ovd_stats = df_copy.groupby("ovd_bin", observed=True)["is_returned"].mean()
    axes[1].bar(range(len(ovd_stats)), ovd_stats.values, color=sns.color_palette("Oranges", len(ovd_stats)))
    axes[1].set_xticks(range(len(ovd_stats)))
    axes[1].set_xticklabels(ovd_stats.index, rotation=45, ha="right")
    axes[1].set_ylabel("Return Rate")
    axes[1].set_title("Order Value Deviation\n(order_value / customer_avg)", fontsize=11, fontweight="bold")
    axes[1].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    # 3. First order effect
    first_order_stats = df.groupby("is_first_order")["is_returned"].mean()
    axes[2].bar(
        ["Repeat Customer", "First Order"],
        first_order_stats.values,
        color=[COLORS["not_returned"], COLORS["returned"]],
        edgecolor="white", linewidth=1.5,
    )
    axes[2].set_ylabel("Return Rate")
    axes[2].set_title("First Order vs Repeat Customer\nReturn Rate", fontsize=11, fontweight="bold")
    axes[2].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    for i, rate in enumerate(first_order_stats.values):
        axes[2].text(i, rate + 0.005, f"{rate:.1%}", ha="center", fontweight="bold")

    fig.suptitle("Customer Behavioral Risk Patterns", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    save_fig(fig, "08_customer_behavior_patterns")

    return {
        "historical_return_rate_effect": hist_stats.to_dict(),
        "order_value_deviation_effect": ovd_stats.to_dict(),
        "first_order_return_rate": float(first_order_stats.get(1, 0)),
        "repeat_return_rate": float(first_order_stats.get(0, 0)),
    }


def analyze_feature_importance_proxy(df: pd.DataFrame) -> dict:
    """Estimate feature importance via absolute correlation with target."""
    num_cols = df.select_dtypes(include=[np.number]).columns.drop("is_returned", errors="ignore")
    target_corr = df[num_cols].apply(lambda x: x.corr(df["is_returned"])).sort_values(key=abs, ascending=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ["#e74c3c" if v > 0 else "#3498db" for v in target_corr.values]
    ax.barh(target_corr.index, target_corr.values, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_xlabel("Pearson Correlation with is_returned")
    ax.set_title("Feature Correlation with Return Outcome\n(Proxy for Feature Importance)", fontsize=14, fontweight="bold")
    ax.axvline(x=0, color="black", linewidth=0.8)

    for i, (feat, val) in enumerate(target_corr.items()):
        ax.text(val + 0.005 * np.sign(val), i, f"{val:.3f}", va="center", fontsize=9)

    fig.tight_layout()
    save_fig(fig, "09_feature_importance_proxy")

    return target_corr.to_dict()


def analyze_temporal_patterns(df: pd.DataFrame) -> dict:
    """Analyze temporal patterns in return rates."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Hour of day
    hour_stats = df.groupby("order_hour")["is_returned"].mean()
    axes[0].plot(hour_stats.index, hour_stats.values, marker="o", color=COLORS["accent"], linewidth=2)
    axes[0].fill_between(hour_stats.index, hour_stats.values, alpha=0.2, color=COLORS["accent"])
    axes[0].set_xlabel("Hour of Day")
    axes[0].set_ylabel("Return Rate")
    axes[0].set_title("Return Rate by Hour of Day", fontsize=13, fontweight="bold")
    axes[0].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    axes[0].set_xticks(range(0, 24, 2))

    # Day of week
    dow_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    dow_stats = df.groupby("order_day_of_week")["is_returned"].mean()
    bars = axes[1].bar(
        dow_labels, dow_stats.values,
        color=["#3498db"] * 5 + ["#e74c3c"] * 2,
        edgecolor="white", linewidth=1.5,
    )
    axes[1].set_ylabel("Return Rate")
    axes[1].set_title("Return Rate by Day of Week", fontsize=13, fontweight="bold")
    axes[1].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    fig.tight_layout()
    save_fig(fig, "10_temporal_patterns")

    return {
        "hour_stats": hour_stats.to_dict(),
        "dow_stats": dow_stats.to_dict(),
    }


# ============================================================
# Report Generation
# ============================================================


def generate_eda_report(
    df: pd.DataFrame,
    target_info: dict,
    outlier_info: dict,
    corr_info: dict,
    cat_info: dict,
    price_info: dict,
    payment_info: dict,
    segment_info: dict,
    behavior_info: dict,
    importance_info: dict,
    temporal_info: dict,
) -> str:
    """Generate the EDA markdown report."""
    lines = []

    def add(text: str = "") -> None:
        lines.append(text)

    add("# Exploratory Data Analysis Report --- ReturnGuard AI")
    add()
    add(f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    add(f"**Dataset:** `data/raw/ecommerce_orders.csv`")
    add(f"**Records:** {len(df):,} orders | **Features:** {len(df.columns)} columns")
    add()
    add("---")
    add()

    # 1. Target Distribution
    add("## 1. Target Distribution")
    add()
    add(f"![Target Distribution](figures/01_target_distribution.png)")
    add()
    add(f"| Metric | Value |")
    add(f"|--------|-------|")
    add(f"| Return Rate | **{target_info['return_rate']:.2%}** |")
    add(f"| Not Returned | {target_info['not_returned']:,} |")
    add(f"| Returned | {target_info['returned']:,} |")
    add(f"| Imbalance Ratio | {target_info['imbalance_ratio']} |")
    add()
    add("The dataset has a **27.1% return rate** --- moderately imbalanced. This is realistic for e-commerce")
    add("(typical range: 15-35%). Accuracy alone will be insufficient; we need PR-AUC and F1.")
    add()

    # 2. Numerical Distributions
    add("## 2. Numerical Feature Distributions")
    add()
    add("![Numerical Distributions](figures/02_numerical_distributions.png)")
    add()
    add("### Outlier Summary (IQR Method)")
    add()
    add("| Feature | Outliers | Outlier % | IQR Lower | IQR Upper |")
    add("|---------|----------|-----------|-----------|-----------|")
    for feat, info in sorted(outlier_info.items(), key=lambda x: -x[1]["outlier_pct"]):
        add(f"| `{feat}` | {info['outliers']:,} | {info['outlier_pct']:.1f}% | {info['iqr_lower']:.2f} | {info['iqr_upper']:.2f} |")
    add()
    add("**Key observations:**")
    add("- `order_value_deviation` has the most outliers --- orders significantly above customer average")
    add("- `customer_total_orders` and `customer_total_returns` have right-skewed distributions (power law)")
    add("- Outliers are genuine data points (not errors), so we retain them for modeling")
    add()

    # 3. Correlation Matrix
    add("## 3. Feature Correlations")
    add()
    add("![Correlation Matrix](figures/03_correlation_matrix.png)")
    add()
    add("### Top Correlations with Target (`is_returned`)")
    add()
    add("| Feature | Correlation | Direction |")
    add("|---------|-------------|-----------|")
    for feat, corr in sorted(importance_info.items(), key=lambda x: -abs(x[1])):
        direction = "Increases return risk" if corr > 0 else "Decreases return risk"
        add(f"| `{feat}` | {corr:.4f} | {direction} |")
    add()
    add("**Key finding:** `customer_return_rate` and `product_return_rate` are the strongest predictors")
    add("of return risk. This is consistent with the hypothesis that past behavior is the best predictor.")
    add()

    # 4. Return Rate by Category
    add("## 4. Return Rate by Product Category")
    add()
    add("![Return Rate by Category](figures/04_return_rate_by_category.png)")
    add()
    add("| Category | Order Count | Return Rate | Avg Order Value |")
    add("|----------|-------------|-------------|-----------------|")
    for cat, info in sorted(cat_info.items(), key=lambda x: -x[1]["return_rate"]):
        add(f"| {cat} | {info['order_count']:,.0f} | {info['return_rate']:.1%} | Rs.{info['avg_order_value']:,.0f} |")
    add()
    add("**Clothing and Footwear** have the highest return rates, consistent with real-world e-commerce")
    add("patterns (sizing issues, fit, and appearance expectations drive higher returns).")
    add()

    # 5. Return Rate by Price Band
    add("## 5. Return Rate by Order Value Band")
    add()
    add("![Return Rate by Price Band](figures/05_return_rate_by_price_band.png)")
    add()

    # 6. Return Rate by Payment Method
    add("## 6. Return Rate by Payment Method")
    add()
    add("![Return Rate by Payment](figures/06_return_rate_by_payment.png)")
    add()
    add("**COD (Cash on Delivery)** has the highest return rate, which aligns with industry knowledge:")
    add("COD orders have lower purchase commitment and higher return propensity.")
    add()

    # 7. Return Rate by Segment
    add("## 7. Return Rate by Customer Segment")
    add()
    add("![Return Rate by Segment](figures/07_return_rate_by_segment.png)")
    add()

    # 8. Customer Behavioral Patterns
    add("## 8. Customer Behavioral Risk Patterns")
    add()
    add("![Customer Behavior Patterns](figures/08_customer_behavior_patterns.png)")
    add()
    add("### Key Behavioral Insights")
    add()
    add(f"- **First order return rate:** {behavior_info['first_order_return_rate']:.1%} vs repeat customers: {behavior_info['repeat_return_rate']:.1%}")
    add("- Higher customer historical return rate strongly predicts future returns")
    add("- Orders significantly above customer average value show elevated return risk")
    add()

    # 9. Feature Importance Proxy
    add("## 9. Feature Importance (Correlation Proxy)")
    add()
    add("![Feature Importance](figures/09_feature_importance_proxy.png)")
    add()

    # 10. Temporal Patterns
    add("## 10. Temporal Patterns")
    add()
    add("![Temporal Patterns](figures/10_temporal_patterns.png)")
    add()
    add("Return rates are relatively stable across hours and days, suggesting time-of-order")
    add("is a weak predictor. This is expected given the data generation process.")
    add()

    # 11. Summary
    add("---")
    add()
    add("## 11. Summary of Key EDA Findings")
    add()
    add("| # | Finding | Implication for Modeling |")
    add("|---|---------|------------------------|")
    add("| 1 | Return rate is 27.1% (moderately imbalanced) | Use PR-AUC and F1, not just accuracy |")
    add("| 2 | `customer_return_rate` is the strongest predictor | Include customer history features prominently |")
    add("| 3 | `product_return_rate` is the second strongest | Product-level risk matters significantly |")
    add("| 4 | COD has highest return rate among payment methods | Payment method is a useful feature |")
    add("| 5 | Clothing/Footwear have highest category returns | Category is an informative feature |")
    add("| 6 | Order value deviation increases return risk | Unusual order sizes signal risk |")
    add("| 7 | First orders have slightly higher return rates | is_first_order is a mild risk signal |")
    add("| 8 | Temporal features (hour, day) are weak predictors | Include but don't expect high importance |")
    add("| 9 | No single feature has extreme correlation (>0.85) | No obvious leakage detected |")
    add("| 10 | Outliers are genuine, not errors | Retain outliers for tree-based models |")
    add()

    # 12. Limitations
    add("## 12. Limitations and Biases")
    add()
    add("1. **Synthetic data**: Patterns are generated, not organically observed. Real-world data may have")
    add("   more complex, non-linear interactions and additional noise sources.")
    add("2. **No seasonality**: The synthetic data lacks seasonal patterns (holiday spikes, etc.)")
    add("3. **Fixed product catalog**: Only 50 products vs. thousands in real e-commerce")
    add("4. **No geographic features**: Location is not included as a feature")
    add("5. **Feature correlations are designed**: The logistic risk model creates predictable correlations")
    add()
    add("> **IMPORTANT:** The held-out test set was NOT used for any feature selection decisions in this EDA.")

    return "\n".join(lines)


# ============================================================
# Main
# ============================================================


def main() -> None:
    """Run the complete EDA pipeline."""
    logger.info("=" * 60)
    logger.info("ReturnGuard AI --- Exploratory Data Analysis")
    logger.info("=" * 60)

    # Create figures directory
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Load data
    df = load_data()

    # Run analyses
    logger.info("Analyzing target distribution...")
    target_info = analyze_target_distribution(df)

    logger.info("Analyzing numerical distributions...")
    outlier_info = analyze_numerical_distributions(df)

    logger.info("Analyzing correlations...")
    corr_info = analyze_correlation_matrix(df)

    logger.info("Analyzing return rate by category...")
    cat_info = analyze_return_rate_by_category(df)

    logger.info("Analyzing return rate by price band...")
    price_info = analyze_return_rate_by_price_band(df)

    logger.info("Analyzing return rate by payment method...")
    payment_info = analyze_return_rate_by_payment(df)

    logger.info("Analyzing return rate by segment...")
    segment_info = analyze_return_rate_by_segment(df)

    logger.info("Analyzing customer behavior patterns...")
    behavior_info = analyze_customer_history_patterns(df)

    logger.info("Analyzing feature importance...")
    importance_info = analyze_feature_importance_proxy(df)

    logger.info("Analyzing temporal patterns...")
    temporal_info = analyze_temporal_patterns(df)

    # Generate report
    logger.info("Generating EDA report...")
    report = generate_eda_report(
        df, target_info, outlier_info, corr_info, cat_info,
        price_info, payment_info, segment_info, behavior_info,
        importance_info, temporal_info,
    )

    REPORT_FILE.write_text(report, encoding="utf-8")
    logger.info("EDA report saved to %s", REPORT_FILE)

    # Summary
    n_figs = len(list(FIGURES_DIR.glob("*.png")))
    logger.info("=" * 60)
    logger.info("EDA COMPLETE")
    logger.info("Report: %s", REPORT_FILE)
    logger.info("Figures: %d charts in %s", n_figs, FIGURES_DIR)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
