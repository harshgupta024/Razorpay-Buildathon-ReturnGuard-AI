# Data Quality & Validation Report — ReturnGuard AI

**Audit Execution Timestamp:** 2026-08-28 21:54:01 UTC
**Dataset Evaluated:** `C:/Harsh Gupta/Project/RazorPay/data/raw/ecommerce_orders.csv`
**Total Records:** 100,000 rows | **Total Features:** 26 columns
**Overall Health Verdict:** ✅ HEALTHY / PRODUCTION-READY

---

## 1. Executive Summary

| Metric | Result | Target Benchmark | Status |
|:---|:---|:---|:---|
| **Total Validation Checks** | **28** | 25+ rigorous checks | ✅ Passed |
| **Passed Checks** | **28** | 100% of hard constraints | ✅ Passed |
| **Failed Checks** | **0** | 0 failures | ✅ Zero failures |
| **Warning Flags** | **0** | 0 critical warnings | ✅ Clear |
| **Completeness Rate** | **100.0%** | 100% non-null | ✅ 0 missing values |
| **Primary Key Uniqueness** | **100.0%** | 100% unique `order_id` | ✅ 0 duplicates |
| **Target Return Rate** | **27.10%** | Realistic retail (15–35%) | ✅ Balanced (27.10%) |
| **Pre-Fulfillment Timing** | **100% Pre-Shipment** | 0 post-fulfillment leakage fields | ✅ Zero leakage |

---

## 2. Detailed Audit Matrix by Category

### Category: Business Logic

| Status | Check Name | Evaluation Finding |
|:---:|:---|:---|
| **✅ PASS** | `Returns <= Total Orders` | Invariant satisfied: customer_total_returns <= customer_total_orders for all records. |
| **✅ PASS** | `Customer Return Rate Consistency` | customer_return_rate matches customer_total_returns / customer_total_orders exactly. |
| **✅ PASS** | `Weekend Indicator Consistency` | is_weekend_order strictly matches order_day_of_week (Saturday=5, Sunday=6). |

### Category: Categorical Domain

| Status | Check Name | Evaluation Finding |
|:---:|:---|:---|
| **✅ PASS** | `Domain: payment_method` | All values belong to permissible domain set (6 categories). |
| **✅ PASS** | `Domain: customer_segment` | All values belong to permissible domain set (4 categories). |
| **✅ PASS** | `Domain: product_category` | All values belong to permissible domain set (8 categories). |

### Category: Completeness

| Status | Check Name | Evaluation Finding |
|:---:|:---|:---|
| **✅ PASS** | `Missing Values` | 0 missing values across all 26 columns (100% complete dataset). |

### Category: Range & Invariants

| Status | Check Name | Evaluation Finding |
|:---:|:---|:---|
| **✅ PASS** | `Range: order_value` | Satisfies order_value > 0. 0 boundary violations. |
| **✅ PASS** | `Range: quantity` | Satisfies 1 <= quantity <= 10. 0 boundary violations. |
| **✅ PASS** | `Range: discount_pct` | Satisfies 0 <= discount_pct <= 100. 0 boundary violations. |
| **✅ PASS** | `Range: customer_account_age_days` | Satisfies customer_account_age_days >= 1. 0 boundary violations. |
| **✅ PASS** | `Range: customer_total_orders` | Satisfies customer_total_orders >= 1. 0 boundary violations. |
| **✅ PASS** | `Range: customer_return_rate` | Satisfies 0.0 <= customer_return_rate <= 1.0. 0 boundary violations. |
| **✅ PASS** | `Range: product_price` | Satisfies product_price > 0. 0 boundary violations. |
| **✅ PASS** | `Range: product_weight_grams` | Satisfies product_weight_grams > 0. 0 boundary violations. |
| **✅ PASS** | `Range: product_return_rate` | Satisfies 0.0 <= product_return_rate <= 1.0. 0 boundary violations. |
| **✅ PASS** | `Range: product_avg_rating` | Satisfies 1.0 <= product_avg_rating <= 5.0. 0 boundary violations. |
| **✅ PASS** | `Range: order_value_deviation` | Satisfies order_value_deviation > 0. 0 boundary violations. |
| **✅ PASS** | `Range: order_hour` | Satisfies 0 <= order_hour <= 23. 0 boundary violations. |
| **✅ PASS** | `Range: order_day_of_week` | Satisfies 0 <= order_day_of_week <= 6. 0 boundary violations. |
| **✅ PASS** | `Range: is_weekend_order` | Satisfies is_weekend_order in {0, 1}. 0 boundary violations. |
| **✅ PASS** | `Range: is_first_order` | Satisfies is_first_order in {0, 1}. 0 boundary violations. |

### Category: Schema

| Status | Check Name | Evaluation Finding |
|:---:|:---|:---|
| **✅ PASS** | `Column Presence` | All 26 expected columns present. Zero unexpected columns. |
| **✅ PASS** | `Data Volume` | Dataset has 100,000 rows (meets >= 50,000 requirement for ML modeling). |

### Category: Target & Leakage

| Status | Check Name | Evaluation Finding |
|:---:|:---|:---|
| **✅ PASS** | `Target Distribution & Balance` | Target is binary (0, 1) with realistic e-commerce return rate: 27.10% (27,098 returns / 100,000 orders). |
| **✅ PASS** | `No Collinear Target Leakage` | No individual feature has |correlation| >= 0.85 with the target. Max correlation is safe. |

### Category: Uniqueness

| Status | Check Name | Evaluation Finding |
|:---:|:---|:---|
| **✅ PASS** | `Primary Key (order_id) Uniqueness` | Every order_id is globally unique (100,000 distinct identifiers). |
| **✅ PASS** | `Entity Coverage` | Covering 9,148 unique customers and 50 unique catalog products. |

---

## 3. Statistical Distribution & Anomaly Profiles

| Feature | Min | Q25 | Median | Mean | Q75 | Max | Std Dev | Zero/Neg Count |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| `order_value` | 199.00 | 2090.00 | 5745.00 | 11808.22 | 12395.25 | 209145.00 | 19787.25 | 0 |
| `quantity` | 1.00 | 1.00 | 2.00 | 2.22 | 3.00 | 5.00 | 1.40 | 0 |
| `discount_pct` | 0.00 | 2.30 | 5.60 | 7.96 | 11.10 | 50.00 | 7.85 | 600 |
| `is_first_order` | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 | 1.00 | 0.17 | 97,086 |
| `customer_account_age_days` | 1.00 | 104.00 | 251.00 | 366.95 | 511.00 | 1825.00 | 361.33 | 0 |
| `customer_total_orders` | 1.00 | 8.00 | 20.00 | 34.08 | 53.00 | 100.00 | 33.41 | 0 |
| `customer_total_returns` | 0.00 | 1.00 | 4.00 | 9.32 | 12.00 | 66.00 | 12.24 | 16,454 |
| `customer_return_rate` | 0.00 | 0.10 | 0.22 | 0.23 | 0.34 | 0.80 | 0.17 | 16,454 |
| `customer_avg_order_value` | 200.00 | 1102.00 | 1775.00 | 2278.32 | 2845.00 | 20000.00 | 1817.91 | 0 |
| `customer_days_since_last_order` | 0.00 | 8.00 | 20.00 | 29.02 | 41.00 | 269.00 | 29.34 | 3,396 |
| `product_price` | 398.00 | 1445.00 | 2961.00 | 5776.66 | 8014.00 | 41829.00 | 7547.67 | 0 |
| `product_weight_grams` | 258.00 | 2327.00 | 4981.00 | 5954.55 | 9959.00 | 14070.00 | 4039.47 | 0 |
| `product_return_rate` | 0.02 | 0.11 | 0.17 | 0.16 | 0.19 | 0.38 | 0.08 | 0 |
| `product_avg_rating` | 2.10 | 3.40 | 3.70 | 3.74 | 4.10 | 5.00 | 0.67 | 0 |
| `order_value_deviation` | 0.02 | 1.08 | 2.94 | 8.63 | 8.08 | 972.52 | 20.55 | 0 |
| `order_hour` | 0.00 | 5.00 | 11.00 | 11.47 | 17.00 | 23.00 | 6.93 | 4,204 |
| `order_day_of_week` | 0.00 | 1.00 | 3.00 | 3.00 | 5.00 | 6.00 | 2.00 | 14,341 |
| `is_weekend_order` | 0.00 | 0.00 | 0.00 | 0.28 | 1.00 | 1.00 | 0.45 | 71,533 |
| `is_returned` | 0.00 | 0.00 | 0.00 | 0.27 | 1.00 | 1.00 | 0.44 | 72,902 |

---

## 4. Categorical Breakdown Profiles

#### `payment_method` Frequency Breakdown

| Category Value | Record Count | Proportion | Return Rate in Segment |
|:---|:---|:---|:---|
| **COD** | 25,000 | 25.00% | 30.87% |
| **Credit Card** | 14,859 | 14.86% | 25.51% |
| **Debit Card** | 11,997 | 12.00% | 25.64% |
| **Net Banking** | 10,001 | 10.00% | 26.09% |
| **UPI** | 30,230 | 30.23% | 25.90% |
| **Wallet** | 7,913 | 7.91% | 26.24% |

#### `customer_segment` Frequency Breakdown

| Category Value | Record Count | Proportion | Return Rate in Segment |
|:---|:---|:---|:---|
| **new** | 1,485 | 1.49% | 23.16% |
| **premium** | 29,378 | 29.38% | 28.90% |
| **regular** | 31,240 | 31.24% | 26.57% |
| **vip** | 37,897 | 37.90% | 26.30% |

#### `product_category` Frequency Breakdown

| Category Value | Record Count | Proportion | Return Rate in Segment |
|:---|:---|:---|:---|
| **Accessories** | 10,109 | 10.11% | 22.93% |
| **Beauty** | 14,007 | 14.01% | 18.65% |
| **Books** | 15,971 | 15.97% | 12.28% |
| **Clothing** | 10,123 | 10.12% | 24.69% |
| **Electronics** | 11,910 | 11.91% | 41.76% |
| **Footwear** | 5,988 | 5.99% | 34.97% |
| **Home** | 10,050 | 10.05% | 39.50% |
| **Sports** | 21,842 | 21.84% | 30.54% |

---

## 5. Pre-Fulfillment Leakage Prevention Audit

To uphold the strict architectural safety boundary, the dataset was audited against forbidden post-fulfillment attributes:

1. **Direct Outcome Fields**: No `return_date`, `refund_status`, `refund_amount`, or `return_reason` fields present.
2. **Logistics & Delivery Fields**: No `delivery_delay`, `delivery_feedback`, `carrier_tracking_status`, or `courier_notes` present.
3. **Customer Support Signals**: No `post_delivery_dispute` or `ticket_id` included prior to fulfillment.
4. **Correlation Ceiling**: Maximum Pearson correlation between any individual pre-fulfillment feature and the return outcome is well below the 0.85 threshold.

---

## 6. Conclusion & Readiness

The data validation pipeline confirms that the dataset meets all criteria for:
- **Clean Preprocessing & Feature Engineering (Phase 3)**
- **Stratified Train / Validation / Test Splitting (Phase 4)**
- **Zero-Leakage Baseline & Advanced ML Model Training (Phases 5–6)**