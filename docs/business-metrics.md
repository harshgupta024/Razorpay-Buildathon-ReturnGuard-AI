# Business Metrics — ReturnGuard AI

## 1. The Business Problem

Product returns are a significant cost center for e-commerce and D2C merchants:

| Cost Component | Description |
|---------------|-------------|
| **Return shipping** | Cost of shipping the product back |
| **Handling & inspection** | Warehouse labor to receive, inspect, restock |
| **Margin erosion** | Lost profit on the sale |
| **Inventory risk** | Returned items may be damaged, out of season, or unsellable |
| **Customer acquisition cost** | If the customer churns, acquisition cost is lost |
| **Operational overhead** | Staff time managing returns process |

## 2. How ReturnGuard Creates Value

ReturnGuard intervenes **before fulfillment** — the last point where the merchant can take a lower-cost action.

### Value Proposition

```
Without ReturnGuard:
  Order → Ship → Deliver → Customer Returns → Full Cost Incurred

With ReturnGuard:
  Order → Risk Assessment → [Approve | Review | Hold] → Informed Decision
```

## 3. Cost Model

> **⚠️ IMPORTANT**: The costs below are configurable assumptions for demonstration purposes. They do NOT represent actual Razorpay pricing or any specific merchant's costs.

### 3.1 Configurable Cost Parameters

| Parameter | Default Value | Description |
|-----------|--------------|-------------|
| `avg_order_value` | ₹3,000 | Average order value |
| `avg_margin_pct` | 30% | Average profit margin percentage |
| `return_shipping_cost` | ₹150 | Cost to ship returned item back |
| `handling_cost` | ₹100 | Warehouse handling per return |
| `restocking_loss_pct` | 10% | Value lost on restocking |
| `manual_review_cost` | ₹50 | Cost of manual order review |
| `estimated_conversion_loss` | ₹200 | Estimated loss from delaying legitimate order |

### 3.2 Cost of a False Negative (Missed Return)

A return that the model failed to flag:

```
FN_cost = return_shipping_cost
        + handling_cost
        + (order_value × restocking_loss_pct)
        + (order_value × avg_margin_pct)    # margin lost

Example:
FN_cost = ₹150 + ₹100 + (₹3,000 × 0.10) + (₹3,000 × 0.30)
        = ₹150 + ₹100 + ₹300 + ₹900
        = ₹1,450
```

### 3.3 Cost of a False Positive (Incorrectly Flagged)

A legitimate order incorrectly flagged as high-risk:

```
FP_cost = manual_review_cost
        + estimated_conversion_loss    # risk of losing the sale

Example:
FP_cost = ₹50 + ₹200
        = ₹250
```

### 3.4 Cost Asymmetry

The cost of a False Negative is typically **much higher** than a False Positive:

```
FN_cost / FP_cost = ₹1,450 / ₹250 = 5.8×
```

This asymmetry is critical for threshold selection: it's usually worth reviewing a few extra legitimate orders to catch more returns.

## 4. Business Metrics

### 4.1 Estimated Return Cost Prevented

```
Prevented_cost = (True Positives) × avg_FN_cost
```

These are returns that the model correctly identified, allowing the merchant to take preventive action.

### 4.2 False Positive Cost Incurred

```
FP_total_cost = (False Positives) × avg_FP_cost
```

These are legitimate orders that were unnecessarily reviewed.

### 4.3 Net Benefit

```
Net_benefit = Prevented_cost - FP_total_cost
```

The system is valuable when `Net_benefit > 0`.

### 4.4 Review Volume

```
Review_volume = (Predicted Positives) / (Total Orders) × 100%
```

Must remain manageable — target: < 30% of orders.

### 4.5 ROI Estimate

```
ROI = Net_benefit / Total_operational_cost × 100%
```

## 5. Threshold-Business Tradeoff

Different thresholds produce different business outcomes:

| Threshold | Precision | Recall | FPR | Review Vol. | Net Benefit |
|-----------|-----------|--------|-----|-------------|-------------|
| 0.20 | Low | High | High | High | May be negative |
| 0.40 | Medium | Medium | Medium | Medium | Often optimal |
| 0.60 | High | Low | Low | Low | May miss returns |
| 0.80 | Very High | Very Low | Very Low | Very Low | Catches few |

The optimal threshold balances:
- **Catching enough returns** (recall) to justify the system
- **Not flagging too many legitimate orders** (precision) to avoid merchant fatigue
- **Net positive business outcome** (benefit > cost)

## 6. Success Metrics for Hackathon

| Metric | Target | How Measured |
|--------|--------|-------------|
| Demonstrates real ML | Actual model with real metrics | Live predictions, not mock data |
| Shows business value | Net benefit > 0 at optimal threshold | Cost engine calculation |
| Actionable for merchants | Clear recommendations | Dashboard review queue |
| Explains decisions | Top risk factors per prediction | SHAP explanations |
| Responsible AI | No fraud accusations, human oversight | Language, override capability |
| Production-ready architecture | Clean API, proper splits, no leakage | Code review |

## 7. Assumptions and Caveats

1. All cost parameters are configurable assumptions, not actual merchant data
2. Actual business impact depends on merchant-specific return rates and costs
3. The model assumes historical patterns continue (no distribution shift)
4. Conversion loss from false positives is estimated, not measured
5. The system provides decision support; actual ROI depends on how recommendations are acted upon
