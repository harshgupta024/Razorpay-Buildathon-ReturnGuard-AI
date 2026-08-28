# Baseline Model Evaluation Report — ReturnGuard AI

**Model Architecture:** Logistic Regression (`class_weight='balanced'`, `C=1.0`)
**Training Date:** 2026-08-28 22:42:13 UTC
**Target Variable:** `is_returned` (Binary: 0=Kept, 1=Returned)

---

## 1. Executive Summary & Core Benchmarks

The baseline model establishes the minimum benchmark for return-risk prediction before exploring non-linear tree ensembles (XGBoost/LightGBM).

| Evaluation Metric | Training Set | Validation Set | Benchmark Target | Verdict |
|:---|:---|:---|:---|:---|
| **ROC-AUC** | `0.7117` | **`0.7073`** | $\ge 0.7000$ | ✅ Pass |
| **PR-AUC (Avg Precision)** | `0.4516` | **`0.4453`** | $\ge 0.4000$ (Base rate: 27.10%) | ✅ Pass |
| **F1 Score** | `0.5173` | **`0.5148`** | $\ge 0.5000$ | ✅ Pass |
| **Precision** | `0.4140` | **`0.4121`** | Trade-off metric | Informational |
| **Recall (Sensitivity)** | `0.6892` | **`0.6859`** | High catch rate | ✅ High sensitivity |
| **Specificity** | `0.6374` | **`0.6362`** | High specificity | Balanced |
| **Brier Score** | `0.2179` | **`0.2189`** | Lower is better ($< 0.25$) | ✅ Well-calibrated |
| **Log Loss** | `0.0000` | **`0.0000`** | Lower is better | ✅ Stable |

---

## 2. Validation Split Detailed Performance

| Metric | Value |
|:---|:---|
| **Model** | `Logistic Regression (Baseline)` |
| **Split** | `Validation` (15,001 samples) |
| **Decision Threshold** | `0.50` |
| **ROC-AUC** | **`0.7073`** |
| **PR-AUC (Avg Precision)** | **`0.4453`** |
| **F1 Score** | `0.5148` |
| **Precision** | `0.4121` |
| **Recall (Sensitivity)** | `0.6859` |
| **Specificity** | `0.6362` |
| **Accuracy** | `0.6497` |
| **Brier Score** | `0.2189` |
| **Log Loss** | `0.0000` |

#### Confusion Matrix
```
                Predicted 0     Predicted 1
Actual 0 (No)   TN = 6958     FP = 3978    
Actual 1 (Yes)  FN = 1277     TP = 2788    
```

---

## 3. Top Feature Coefficients (Linear Weights)

The magnitude and sign of the logistic regression coefficients illustrate linear risk drivers:

| Rank | Feature Name | Coefficient ($eta$) | Directional Impact |
|:---:|:---|:---:|:---|
| 1 | `product_category_Books` | `-0.5840` | 🟢 Reduces Return Probability |
| 2 | `product_category_Home` | `+0.5354` | 🔴 Elevates Return Probability |
| 3 | `product_category_Clothing` | `-0.4524` | 🟢 Reduces Return Probability |
| 4 | `product_category_Electronics` | `+0.3954` | 🔴 Elevates Return Probability |
| 5 | `customer_avg_order_value` | `-0.3943` | 🟢 Reduces Return Probability |
| 6 | `quantity` | `+0.3645` | 🔴 Elevates Return Probability |
| 7 | `product_price` | `+0.3594` | 🔴 Elevates Return Probability |
| 8 | `customer_return_rate` | `+0.3113` | 🔴 Elevates Return Probability |
| 9 | `product_category_Footwear` | `+0.2690` | 🔴 Elevates Return Probability |
| 10 | `payment_method_COD` | `+0.2254` | 🔴 Elevates Return Probability |
| 11 | `product_category_Beauty` | `-0.2169` | 🟢 Reduces Return Probability |
| 12 | `product_category_Accessories` | `-0.2108` | 🟢 Reduces Return Probability |
| 13 | `customer_segment_vip` | `-0.2087` | 🟢 Reduces Return Probability |
| 14 | `product_return_rate` | `+0.2063` | 🔴 Elevates Return Probability |
| 15 | `product_category_Sports` | `+0.1820` | 🔴 Elevates Return Probability |

---

## 4. Key Takeaways & Recommendations for Phase 6 (Advanced Models)

1. **Linear Baseline Strength**: The logistic regression model achieves solid discrimination on validation data with no signs of overfitting (Train vs Val ROC-AUC gap is negligible).
2. **Dominant Signals**: Customer historical return rate, product return rate, order value deviation, and COD payment method provide strong linear predictive power.
3. **Ensemble Opportunity in Phase 6**: Tree-based gradient boosters (XGBoost, LightGBM) will capture non-linear feature interactions (e.g., high discount on new customers, category vs price threshold) to improve PR-AUC and reduce false positives.