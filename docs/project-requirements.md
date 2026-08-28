# Project Requirements — ReturnGuard AI

## 1. Problem Statement

E-commerce and D2C merchants face significant revenue loss from product returns. Traditional approaches handle returns reactively — after the product has been shipped, delivered, and returned — absorbing the full cost of reverse logistics, handling, restocking, and margin erosion.

**ReturnGuard AI** addresses this by predicting return probability **before fulfillment**, giving merchants an opportunity to take cost-aware actions (review, hold, verify) before incurring irrecoverable costs.

## 2. Target Users

| User | Role |
|------|------|
| E-commerce merchants | Decision-makers who approve/hold orders |
| D2C brand operators | Owners managing margins and return costs |
| Risk analysts | Professionals reviewing flagged orders |
| Operations teams | Staff managing fulfillment workflows |
| Fulfillment teams | Teams processing shipments |

## 3. Scope

### In Scope

- Return probability prediction for individual orders **before fulfillment**
- Risk level classification (LOW / MEDIUM / HIGH)
- Feature-based explanation of risk factors
- Configurable business cost model (false positive vs. false negative costs)
- Recommended operational actions (Approve / Manual Review / Hold)
- Human-in-the-loop review and override
- Analytics dashboard (risk distribution, model performance, business impact)
- ML model evaluation with proper train/validation/test methodology
- Threshold optimization based on business objectives
- Model card and responsible AI documentation

### Out of Scope (Non-Goals)

- **Fraud detection / fraud accusation** — This system predicts return risk, not fraud
- **Automatic order rejection** — All actions are recommendations; humans decide
- **Payment fraud tools** — No offensive security capabilities
- **Customer scoring for marketing** — Not a CRM tool
- **Real-time payment gateway integration** — MVP uses API endpoints
- **Multi-tenant SaaS deployment** — Single-instance MVP
- **Mobile application** — Web dashboard only
- **Natural language chatbot** — Dashboard-based interaction

## 4. Assumptions

1. Historical order data with return outcomes is available (public dataset or synthetic)
2. Sufficient pre-fulfillment features exist to build a useful predictive model
3. The cost of false positives (flagging legitimate orders) and false negatives (missing returns) can be estimated with configurable parameters
4. Merchants are willing to incorporate ML-assisted review into their workflow
5. A single ML model can serve the MVP; per-category or per-merchant models are future work
6. SQLite is sufficient for MVP data storage

## 5. Success Criteria

### ML Success Criteria

| Metric | Target | Rationale |
|--------|--------|-----------|
| ROC-AUC | ≥ 0.75 | Demonstrates meaningful signal above random |
| PR-AUC | ≥ 0.50 | Important for imbalanced classes |
| Precision (at operating threshold) | ≥ 0.60 | Limits false positive burden |
| Recall (at operating threshold) | ≥ 0.50 | Catches meaningful fraction of returns |
| Calibration | Reasonably calibrated | Probabilities should approximate true rates |

### Business Success Criteria

| Criterion | Definition |
|-----------|------------|
| Net cost benefit | Estimated prevented return cost > cost of false positives |
| Actionable recommendations | ≥ 80% of HIGH risk predictions have clear, explainable factors |
| Review volume manageable | Operating threshold keeps review queue < 30% of orders |
| Human override capability | 100% of recommendations can be overridden |

## 6. Safety Requirements

1. **Defensive only** — No fraud generation, attack automation, or offensive capabilities
2. **No customer accusations** — System uses risk-appropriate language only
3. **Human oversight** — Every recommendation can be overridden
4. **Transparency** — Risk factors are explained to the analyst
5. **Data minimization** — No unnecessary personal information stored
6. **No gaming exposure** — Explanations avoid revealing exploitable thresholds
7. **Clear labeling** — Synthetic/demo data is always clearly marked
8. **Probability, not certainty** — All outputs are presented as estimates

## 7. Key User Stories

### US-01: View Risk Dashboard
> As a merchant, I want to see an overview of return-risk statistics so I can understand my exposure.

### US-02: Inspect Order Risk
> As a risk analyst, I want to see the return probability, risk level, and explanation for a specific order so I can decide how to process it.

### US-03: Override Recommendation
> As a merchant, I want to override the model's recommendation with my own decision and record the reason.

### US-04: Understand Risk Factors
> As an operations manager, I want to see why an order was flagged as high-risk so I can take appropriate action.

### US-05: Estimate Financial Impact
> As a merchant, I want to see the estimated cost of a potential return so I can weigh it against the cost of delaying the order.

### US-06: Review Model Performance
> As a risk analyst, I want to see precision, recall, and other metrics to understand how reliable the model is.

### US-07: Analyze Trends
> As a merchant, I want to see return rates by category, price band, and other dimensions to identify systemic issues.

### US-08: Review False Positives
> As a risk analyst, I want to identify and review false positives so I can understand the model's limitations.
