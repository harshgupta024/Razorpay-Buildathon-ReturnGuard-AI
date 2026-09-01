# ReturnGuard AI — Official Model Card & Responsible AI Specification

**Model Version:** `v1.0.0`  
**Standard Compliance:** Mitchell et al. (2019) *Model Cards for Model Reporting*  
**Deployment Context:** Razorpay Buildathon 2026 — Track 02 (E-Commerce Risk Intelligence)  
**Governance Status:** Approved for Production Deployment  

---

## 1. Model Details

- **Model Name:** ReturnGuard AI Production Estimator
- **Model Type:** Scikit-Learn `HistGradientBoostingClassifier` wrapped in 5-Fold Cross-Validated `CalibratedClassifierCV(method='isotonic')`
- **Feature Preprocessor:** `FeaturePreprocessor` combining `StandardScaler` (18 continuous/discrete numeric signals) and `OneHotEncoder` (3 categorical signals: `product_category`, `payment_method`, `customer_segment`), producing a 36-dimensional feature vector.
- **Inference Latency:** `0.002 ms` per order (vectorized batch throughput `> 15,000 orders/sec`).
- **Primary Artifacts:**
  - `models/preprocessor.joblib` (5.2 KB)
  - `models/champion_model.joblib` (670 KB)
  - `models/calibrated_model.joblib` (3.4 MB)

---

## 2. Intended Use & Ethical Boundaries

### Primary Intended Use Case
- Real-time pre-fulfillment risk scoring of e-commerce orders at the point of checkout.
- Automated recommendation of cost-optimal merchant interventions (e.g. WhatsApp size confirmation, ₹100 COD shipping deposit, address validation).
- Routing high-stakes orders to a dedicated merchant human-in-the-loop review queue.

### Out-of-Scope & Strictly Prohibited Uses
1. **No Accusatory Labeling:** The model MUST NOT be used to label human consumers as "fraudsters", "abusers", "criminals", or "dishonest".
2. **No Arbitrary Blacklisting:** The model MUST NOT be used to permanently ban consumers from shopping without clear human review.
3. **No Cross-Merchant Data Leakage:** Customer behavior on one merchant cannot be shared with competitor merchants without explicit customer consent.
4. **No Post-Fulfillment Leakage:** Zero post-fulfillment signals (delivery time, carrier tracking, refund status) are ever used during scoring.

---

## 3. Training, Validation & Evaluation Data

- **Dataset Size:** 100,000 e-commerce order records with 26 feature columns.
- **Split Strategy:** 70% Train (70,000), 15% Validation (15,001), 15% Held-Out Test (15,000) with exact stratified 27.10% target preservation.
- **Data Quality Invariants:** 28 automated checks passed (zero nulls, non-negative prices, returns $\le$ total orders, zero post-fulfillment leakage).

---

## 4. Quantitative Evaluation Benchmarks

| Metric | Train Partition | Validation Partition | Locked Test Partition | Status |
|:---|:---:|:---:|:---:|:---:|
| **ROC-AUC** | 0.7480 | 0.7314 | **0.7345** | ✅ Target Met (>0.70) |
| **PR-AUC** | 0.4990 | 0.4779 | **0.4845** | ✅ Target Met (>0.45) |
| **Expected Calibration Error (ECE)** | 0.0035 | 0.0086 | **0.0041 (0.41%)** | ✅ Target Met (<1.0%) |
| **Brier Score** | 0.1680 | 0.1716 | **0.1706** | ✅ Target Met (<0.18) |
| **Recall @ τ = 0.20** | 80.2% | 79.5% | **79.5%** | ✅ Target Met (>75%) |
| **Net Savings vs Baseline** | ₹5.6M | ₹1.19M | **₹1.19M** | ✅ Target Met (>₹1.0M) |

---

## 5. Fairness & Sub-Group Disparity Analysis

Fairness audits were conducted across customer tiers and product categories on the held-out test split:

### Customer Segment Parity
| Customer Segment | Sample Share | Base Return Rate | Model Predicted Avg Risk | Subgroup ROC-AUC |
|:---|:---:|:---:|:---:|:---:|
| `new` | 24.8% | 29.2% | 28.9% | **0.7290** |
| `regular` | 50.1% | 26.8% | 26.9% | **0.7360** |
| `premium` | 19.9% | 25.4% | 25.5% | **0.7341** |
| `vip` | 5.2% | 23.1% | 23.4% | **0.7395** |

> **Fairness Finding:** Max ROC-AUC disparity across customer segments is **0.0105** (within the 0.03 tolerance threshold), indicating equitable risk calibration across customer tenures.

---

## 6. Explainability & Human-in-the-Loop Safeguards

1. **SHAP Attributions:** Every prediction generates exact feature-level attributions decomposed into positive risk drivers and protective mitigating signals.
2. **Plain-Language Reason Codes:** Replaces technical coefficients with merchant-friendly, objective phrasing (e.g. *"Order total is 2.8x higher than customer's average order value"*).
3. **Merchant Overrides:** High and Critical risk orders route to the `/api/v1/review` queue where merchants can manually approve, contact, or modify fulfillment policies with immutable audit logging.

---

## 7. Model Governance & Maintenance Plan

- **Drift Monitoring:** Monthly computation of Population Stability Index (PSI) and Wasserstein distance on input features.
- **Retraining Trigger:** Model retraining is triggered if PSI $> 0.15$ or Brier Score drifts $> 0.21$.
- **Model Card Maintenance:** Updated with every major version release.
