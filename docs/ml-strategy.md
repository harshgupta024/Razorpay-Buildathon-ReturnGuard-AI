# ML Strategy — ReturnGuard AI

## 1. Problem Formulation

**Task**: Binary classification  
**Target**: Will this order be returned? (1 = returned, 0 = not returned)  
**Prediction time**: Before fulfillment (pre-shipment)  
**Output**: Calibrated probability of return + risk level

## 2. Feature Strategy

### 2.1 Feature Timing Classification

Every candidate feature must be classified:

| Classification | Definition | Usable? |
|---------------|------------|---------|
| **PRE-FULFILLMENT** | Available at order time, before shipment | ✅ Yes |
| **POST-FULFILLMENT** | Only available after delivery/return | ❌ No (leakage) |

### 2.2 Expected Feature Categories

#### Customer Features (PRE-FULFILLMENT)
- Customer segment / tier
- Account age
- Historical order count
- Historical return count
- Historical return rate
- Average order value
- Days since last order

#### Product Features (PRE-FULFILLMENT)
- Product category
- Product price
- Historical return rate for this product/category
- Product weight (if available)

#### Order Features (PRE-FULFILLMENT)
- Order value
- Number of items
- Payment method
- Discount applied
- Order-value deviation from customer average
- Day of week / time of day
- Is first order?

#### Behavioral Features (PRE-FULFILLMENT)
- Ratio of order value to customer average
- Frequency of recent orders
- Category match with previous purchases

### 2.3 Forbidden Features (POST-FULFILLMENT — LEAKAGE)

- Return date
- Return reason (entered after return)
- Refund amount
- Refund status
- Return shipment tracking
- Post-delivery complaint
- Warehouse inspection result
- Delivery satisfaction score

## 3. Modeling Strategy

### 3.1 Baseline

| Model | Purpose |
|-------|---------|
| **Logistic Regression** | Interpretable baseline, sanity check |

### 3.2 Advanced Candidates

| Model | Strengths | Considerations |
|-------|-----------|---------------|
| **XGBoost** | Strong performance, handles mixed features | Needs tuning, less interpretable |
| **LightGBM** | Fast training, memory-efficient | Similar to XGBoost |
| **Random Forest** | Robust, less prone to overfitting | Slower inference |
| **HistGradientBoosting** | Native sklearn, handles NaN | Good alternative |

### 3.3 Model Selection Criteria

1. **PR-AUC** (primary) — most important for imbalanced classification
2. **ROC-AUC** — overall discriminative ability
3. **F1 at operating threshold** — balanced precision/recall
4. **Calibration quality** — for reliable probability display
5. **Inference speed** — for production API latency
6. **Interpretability** — for SHAP explanations

## 4. Evaluation Strategy

### 4.1 Why Accuracy Is Insufficient

If the return rate is 20%, a model that predicts "no return" for every order achieves 80% accuracy but is completely useless. We need metrics that account for class imbalance.

### 4.2 Primary Metrics

| Metric | Why It Matters |
|--------|---------------|
| **Precision** | What fraction of flagged orders actually get returned? |
| **Recall** | What fraction of actual returns did we catch? |
| **F1** | Harmonic mean of precision and recall |
| **PR-AUC** | Overall precision-recall performance across thresholds |
| **ROC-AUC** | Overall discriminative ability |
| **False Positive Rate** | How many legitimate orders are incorrectly flagged? |
| **False Negative Rate** | How many returns slip through undetected? |

### 4.3 Business Metrics

| Metric | Definition |
|--------|------------|
| Expected false positive cost | FP count × average review/delay cost |
| Expected false negative cost | FN count × average return cost |
| Net benefit | Prevented return cost − false positive cost |
| Review volume | Fraction of orders requiring manual review |

## 5. Data Splitting Protocol

```
Full Dataset
     │
     ├── 70% Training Set    ← Model training
     ├── 15% Validation Set  ← Hyperparameter tuning, threshold selection
     └── 15% Test Set        ← ONE-TIME final evaluation (Phase 16 only)
```

**Rules:**
1. Stratified split to preserve class distribution
2. Consider time-based split if temporal patterns exist
3. Test set is **locked** until Phase 16
4. No feature selection using test set
5. No threshold tuning using test set

## 6. Threshold Optimization Strategy

The default 0.5 threshold is almost never optimal for business use.

**Process:**
1. Sweep thresholds from 0.10 to 0.90 (step 0.05)
2. For each threshold, compute precision, recall, F1, FPR, review volume
3. For each threshold, compute expected business cost (using cost engine)
4. Select threshold that minimizes total expected cost (FP cost + FN cost)
5. Consider secondary constraint: review volume must be manageable

## 7. Probability Calibration Strategy

Raw model probabilities (especially from tree ensembles) may not be well-calibrated.

**Process:**
1. Plot reliability diagram (calibration curve)
2. Compute Expected Calibration Error (ECE)
3. If poorly calibrated, apply Platt Scaling or Isotonic Regression
4. Re-evaluate calibration
5. Document limitations of probability estimates

## 8. Explainability Strategy

**Tool**: SHAP (SHapley Additive exPlanations)

**Per-prediction output:**
- Top 3-5 contributing features with direction (+/-)
- Human-readable descriptions (not raw feature names)

**Global output:**
- Feature importance ranking
- Feature importance plot

**Safety consideration:**
- Do not expose exact thresholds or decision boundaries
- Do not provide information that facilitates gaming the system

## 9. Reproducibility

- **Random seed**: Fixed (e.g., `RANDOM_SEED = 42`)
- **Environment**: `requirements.txt` with pinned versions
- **Data versioning**: SHA-256 hash of raw data
- **Model artifacts**: Saved with metadata (version, training date, metrics)
- **Experiment tracking**: Results logged in structured format

## 10. Known Limitations

1. Model trained on historical patterns — distribution shift will degrade performance
2. Single model for all categories — per-category models may perform better
3. Synthetic data (if used) will not perfectly represent real-world distributions
4. SHAP explanations are approximations, not causal explanations
5. Probability calibration may degrade on out-of-distribution inputs
6. No online learning — model is static until retrained
