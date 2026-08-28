# Dataset Selection — ReturnGuard AI

## 1. Search Process

Public dataset sources searched on 2026-08-28:

| Source | Queries |
|--------|---------|
| Kaggle | "e-commerce returns", "product return prediction", "order return likelihood" |
| UCI ML Repository | "online retail", "e-commerce returns" |
| Google Dataset Search | "e-commerce return prediction dataset" |
| GitHub | "e-commerce return dataset CSV" |

## 2. Candidate Dataset Comparison

| Dataset | Source | Rows | Cols | Return Target | Customer Features | Product Features | Leakage Risk | License | Suitability |
|---------|--------|------|------|---------------|-------------------|------------------|--------------|---------|-------------|
| UCI Online Retail II | UCI ML Repository | ~1M transactions | 8 | ❌ Cancellations only (InvoiceNo starts with 'C') | ⚠️ CustomerID only, no history features | ⚠️ StockCode + Description only | Low | CC BY 4.0 | ❌ Low — no return target, lacks customer/product features |
| E-Commerce Shipping Dataset (prachi13) | Kaggle | 10,999 | 12 | ❌ On-time delivery (not returns) | ⚠️ Limited (prior_purchases, gender) | ⚠️ Cost, weight, importance | Low | CC0 | ❌ Low — target is delivery timing, not returns |
| Synthetic E-Commerce Return Analysis (sayalikhot) | Kaggle | 10,000 | ~10 | ✅ Return_Status | ⚠️ Basic | ⚠️ Basic | ⚠️ May include post-fulfillment fields (Days_to_Return) | CC0 | ⚠️ Medium — synthetic, small, limited features |
| E-Commerce Product Return Likelihood | Kaggle | ~5,000 | ~12 | ✅ Return likelihood | ⚠️ Basic | ⚠️ Price, discount, rating | ⚠️ May include delivery_time (post-fulfillment) | Unknown | ⚠️ Medium — synthetic, small, leakage risk |
| E-Commerce Customer Behavior & Sales 2020-2026 | Kaggle | 25,000 orders | Multiple files | ⚠️ Aggregate return rates in product_summary, not per-order | ✅ RFM metrics, customer profiles | ✅ Categories, ratings | Medium | CC0 | ⚠️ Medium — no per-order return target |
| Ecommerce Customer Behavior (Faker-based) | Kaggle | 50,000 | ~25 | ⚠️ Churn/return binary | ⚠️ Demographics, basic history | ⚠️ Categories, amounts | Unknown | Various | ⚠️ Medium — synthetic, unclear return definition |

## 3. Evaluation Summary

### Why No Public Dataset is Suitable

After evaluating all candidates:

1. **UCI Online Retail II**: Real data, but the target is cancellation (invoice starts with 'C'), not product return. It also lacks customer features (return history, order count, etc.) and product features (category, return rate) needed for rich return-risk prediction. Would require extensive engineering to construct a return proxy, with dubious validity.

2. **Kaggle return-prediction datasets**: All are **already synthetic**. They are small (5K-10K rows), have limited feature sets, and several contain post-fulfillment leakage fields (e.g., `Days_to_Return`, `Delivery_Time`) that would need to be carefully excluded.

3. **E-Commerce Customer Behavior & Sales 2020-2026**: Most promising in terms of feature richness (RFM metrics, product summaries), but return rates are only available at the product-summary level, not per-order. Cannot construct a per-order return target.

### Decision

**Generate a custom synthetic dataset** because:

- No public dataset provides all three requirements: (a) per-order return target, (b) rich pre-fulfillment features, (c) sufficient rows for meaningful ML
- All existing "return prediction" datasets on Kaggle are already synthetic anyway
- A custom generator allows us to control feature distributions, inject realistic patterns, and ensure proper pre/post-fulfillment separation
- We can generate 100,000+ rows for robust ML experiments

## 4. Synthetic Dataset Strategy

> **This dataset is synthetically generated for demonstration and research purposes because a sufficiently suitable public dataset with per-order return targets and rich pre-fulfillment features could not be identified.**

### Design Principles

1. **Realistic distributions** — Feature distributions modeled on e-commerce patterns
2. **Meaningful correlations** — Return probability influenced by logical risk factors
3. **No post-fulfillment leakage** — Every feature available before shipment
4. **Imbalanced target** — ~20-25% return rate (realistic for e-commerce)
5. **Fixed random seed** — Full reproducibility (seed=42)
6. **Sufficient scale** — 100,000 orders from 10,000 customers across 50 products

### Target: 100,000 orders

### Feature Schema

See [data-provenance.md](data-provenance.md) for complete schema.
