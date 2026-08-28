# Data Inspection Report — ReturnGuard AI

**Generated:** 2026-08-28 13:39
**Source file:** `ecommerce_orders.csv`

## 1. Dataset Shape

| Metric | Value |
|--------|-------|
| Rows | 100,000 |
| Columns | 26 |
| File size | 15.00 MB |

## 2. Column Overview

| # | Column | Type | Non-Null | Missing | Unique | Sample |
|---|--------|------|----------|---------|--------|--------|
| 1 | `order_id` | object | 100,000 | 0 | 100,000 | ORD-038273 |
| 2 | `customer_id` | object | 100,000 | 0 | 9,148 | CUST-06236 |
| 3 | `product_id` | object | 100,000 | 0 | 50 | PROD-016 |
| 4 | `order_date` | datetime64[ns] | 100,000 | 0 | 99,916 | 2024-01-01 00:11:42 |
| 5 | `order_value` | float64 | 100,000 | 0 | 20,359 | 3732.0 |
| 6 | `quantity` | int64 | 100,000 | 0 | 5 | 3 |
| 7 | `discount_pct` | float64 | 100,000 | 0 | 500 | 13.9 |
| 8 | `payment_method` | object | 100,000 | 0 | 6 | UPI |
| 9 | `is_first_order` | int64 | 100,000 | 0 | 2 | 0 |
| 10 | `customer_account_age_days` | int64 | 100,000 | 0 | 1,327 | 156 |
| 11 | `customer_total_orders` | int64 | 100,000 | 0 | 94 | 41 |
| 12 | `customer_total_returns` | int64 | 100,000 | 0 | 59 | 19 |
| 13 | `customer_return_rate` | float64 | 100,000 | 0 | 430 | 0.4634 |
| 14 | `customer_avg_order_value` | float64 | 100,000 | 0 | 4,060 | 2036.0 |
| 15 | `customer_segment` | object | 100,000 | 0 | 4 | vip |
| 16 | `customer_days_since_last_order` | int64 | 100,000 | 0 | 194 | 22 |
| 17 | `product_category` | object | 100,000 | 0 | 8 | Sports |
| 18 | `product_price` | float64 | 100,000 | 0 | 49 | 1445.0 |
| 19 | `product_weight_grams` | int64 | 100,000 | 0 | 50 | 10849 |
| 20 | `product_return_rate` | float64 | 100,000 | 0 | 45 | 0.204 |
| 21 | `product_avg_rating` | float64 | 100,000 | 0 | 19 | 3.4 |
| 22 | `order_value_deviation` | float64 | 100,000 | 0 | 24,995 | 1.833 |
| 23 | `order_hour` | int64 | 100,000 | 0 | 24 | 0 |
| 24 | `order_day_of_week` | int64 | 100,000 | 0 | 7 | 0 |
| 25 | `is_weekend_order` | int64 | 100,000 | 0 | 2 | 0 |
| 26 | `is_returned` | int64 | 100,000 | 0 | 2 | 0 |

## 3. Missing Values

✅ **No missing values found.**

## 4. Duplicate Rows

Duplicate rows: **0**

Duplicate order_ids: **0**

## 5. Target Distribution (`is_returned`)

| Value | Label | Count | Percentage |
|-------|-------|-------|------------|
| 0 | Not Returned | 72,902 | 72.9% |
| 1 | Returned | 27,098 | 27.1% |

**Class ratio (returned:not):** 1:2.69

## 6. Numerical Feature Statistics

| Feature | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|---------|-------|------|-----|-----|-----|-----|-----|-----|
| `order_value` | 100000 | 11808.22 | 19787.25 | 199.00 | 2090.00 | 5745.00 | 12395.25 | 209145.00 |
| `quantity` | 100000 | 2.22 | 1.40 | 1.00 | 1.00 | 2.00 | 3.00 | 5.00 |
| `discount_pct` | 100000 | 7.96 | 7.85 | 0.00 | 2.30 | 5.60 | 11.10 | 50.00 |
| `is_first_order` | 100000 | 0.03 | 0.17 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| `customer_account_age_days` | 100000 | 366.95 | 361.33 | 1.00 | 104.00 | 251.00 | 511.00 | 1825.00 |
| `customer_total_orders` | 100000 | 34.08 | 33.41 | 1.00 | 8.00 | 20.00 | 53.00 | 100.00 |
| `customer_total_returns` | 100000 | 9.32 | 12.24 | 0.00 | 1.00 | 4.00 | 12.00 | 66.00 |
| `customer_return_rate` | 100000 | 0.23 | 0.17 | 0.00 | 0.10 | 0.22 | 0.34 | 0.80 |
| `customer_avg_order_value` | 100000 | 2278.32 | 1817.91 | 200.00 | 1102.00 | 1775.00 | 2845.00 | 20000.00 |
| `customer_days_since_last_order` | 100000 | 29.02 | 29.34 | 0.00 | 8.00 | 20.00 | 41.00 | 269.00 |
| `product_price` | 100000 | 5776.66 | 7547.67 | 398.00 | 1445.00 | 2961.00 | 8014.00 | 41829.00 |
| `product_weight_grams` | 100000 | 5954.55 | 4039.47 | 258.00 | 2327.00 | 4981.00 | 9959.00 | 14070.00 |
| `product_return_rate` | 100000 | 0.16 | 0.08 | 0.02 | 0.11 | 0.17 | 0.19 | 0.38 |
| `product_avg_rating` | 100000 | 3.74 | 0.67 | 2.10 | 3.40 | 3.70 | 4.10 | 5.00 |
| `order_value_deviation` | 100000 | 8.63 | 20.55 | 0.02 | 1.08 | 2.94 | 8.08 | 972.52 |
| `order_hour` | 100000 | 11.47 | 6.93 | 0.00 | 5.00 | 11.00 | 17.00 | 23.00 |
| `order_day_of_week` | 100000 | 3.00 | 2.00 | 0.00 | 1.00 | 3.00 | 5.00 | 6.00 |
| `is_weekend_order` | 100000 | 0.28 | 0.45 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 |
| `is_returned` | 100000 | 0.27 | 0.44 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 |

## 7. Categorical Feature Distributions

### `payment_method`

| Value | Count | Percentage |
|-------|-------|------------|
| UPI | 30,230 | 30.2% |
| COD | 25,000 | 25.0% |
| Credit Card | 14,859 | 14.9% |
| Debit Card | 11,997 | 12.0% |
| Net Banking | 10,001 | 10.0% |
| Wallet | 7,913 | 7.9% |

### `customer_segment`

| Value | Count | Percentage |
|-------|-------|------------|
| vip | 37,897 | 37.9% |
| regular | 31,240 | 31.2% |
| premium | 29,378 | 29.4% |
| new | 1,485 | 1.5% |

### `product_category`

| Value | Count | Percentage |
|-------|-------|------------|
| Sports | 21,842 | 21.8% |
| Books | 15,971 | 16.0% |
| Beauty | 14,007 | 14.0% |
| Electronics | 11,910 | 11.9% |
| Clothing | 10,123 | 10.1% |
| Accessories | 10,109 | 10.1% |
| Home | 10,050 | 10.1% |
| Footwear | 5,988 | 6.0% |

## 8. Return Rate by Key Dimensions

### By `product_category`

| Value | Return Rate | Order Count |
|-------|-------------|-------------|
| Electronics | 41.8% | 11,910 |
| Home | 39.5% | 10,050 |
| Footwear | 35.0% | 5,988 |
| Sports | 30.5% | 21,842 |
| Clothing | 24.7% | 10,123 |
| Accessories | 22.9% | 10,109 |
| Beauty | 18.6% | 14,007 |
| Books | 12.3% | 15,971 |

### By `payment_method`

| Value | Return Rate | Order Count |
|-------|-------------|-------------|
| COD | 30.9% | 25,000 |
| Wallet | 26.2% | 7,913 |
| Net Banking | 26.1% | 10,001 |
| UPI | 25.9% | 30,230 |
| Debit Card | 25.6% | 11,997 |
| Credit Card | 25.5% | 14,859 |

### By `customer_segment`

| Value | Return Rate | Order Count |
|-------|-------------|-------------|
| premium | 28.9% | 29,378 |
| regular | 26.6% | 31,240 |
| vip | 26.3% | 37,897 |
| new | 23.2% | 1,485 |

## 9. ID Uniqueness

| ID Column | Total | Unique | Duplicates |
|-----------|-------|--------|------------|
| `order_id` | 100,000 | 100,000 | 0 |
| `customer_id` | 100,000 | 9,148 | 90,852 |
| `product_id` | 100,000 | 50 | 99,950 |

## 10. Feature Timing Classification

| Feature | Classification | Usable for Prediction? |
|---------|---------------|----------------------|
| `order_id` | ✅ PRE-FULFILLMENT | Yes |
| `customer_id` | ✅ PRE-FULFILLMENT | Yes |
| `product_id` | ✅ PRE-FULFILLMENT | Yes |
| `order_date` | ✅ PRE-FULFILLMENT | Yes |
| `order_value` | ✅ PRE-FULFILLMENT | Yes |
| `quantity` | ✅ PRE-FULFILLMENT | Yes |
| `discount_pct` | ✅ PRE-FULFILLMENT | Yes |
| `payment_method` | ✅ PRE-FULFILLMENT | Yes |
| `is_first_order` | ✅ PRE-FULFILLMENT | Yes |
| `customer_account_age_days` | ✅ PRE-FULFILLMENT | Yes |
| `customer_total_orders` | ✅ PRE-FULFILLMENT | Yes |
| `customer_total_returns` | ✅ PRE-FULFILLMENT | Yes ⚠️ (review needed) |
| `customer_return_rate` | ✅ PRE-FULFILLMENT | Yes ⚠️ (review needed) |
| `customer_avg_order_value` | ✅ PRE-FULFILLMENT | Yes |
| `customer_segment` | ✅ PRE-FULFILLMENT | Yes |
| `customer_days_since_last_order` | ✅ PRE-FULFILLMENT | Yes |
| `product_category` | ✅ PRE-FULFILLMENT | Yes |
| `product_price` | ✅ PRE-FULFILLMENT | Yes |
| `product_weight_grams` | ✅ PRE-FULFILLMENT | Yes |
| `product_return_rate` | ✅ PRE-FULFILLMENT | Yes ⚠️ (review needed) |
| `product_avg_rating` | ✅ PRE-FULFILLMENT | Yes |
| `order_value_deviation` | ✅ PRE-FULFILLMENT | Yes |
| `order_hour` | ✅ PRE-FULFILLMENT | Yes |
| `order_day_of_week` | ✅ PRE-FULFILLMENT | Yes |
| `is_weekend_order` | ✅ PRE-FULFILLMENT | Yes |
| `is_returned` | **TARGET** | N/A (this is what we predict) |

## 11. Leakage Analysis

### Features requiring careful review

| Feature | Risk | Justification |
|---------|------|---------------|
| `customer_return_rate` | ⚠️ Low | Historical aggregate — computed BEFORE this order. Acceptable if time-based. |
| `customer_total_returns` | ⚠️ Low | Historical count — same as above. |
| `product_return_rate` | ⚠️ Low | Historical product-level aggregate. Acceptable if computed from prior orders. |

### Confirmed NO post-fulfillment features in dataset

The following features are deliberately **excluded** from the dataset:
- Return date, Return reason, Refund amount, Refund status
- Delivery date, Delivery satisfaction, Post-delivery complaint
- Return shipment tracking, Warehouse inspection result

## 12. Suspicious Patterns

✅ **No suspicious patterns detected.** All values within expected ranges.
