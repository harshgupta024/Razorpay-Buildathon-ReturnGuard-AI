# Architecture — ReturnGuard AI

## 1. System Overview

ReturnGuard AI is a **monolithic MVP** with cleanly separated layers:

```
┌─────────────────────────────────────────────────────────┐
│                    REACT DASHBOARD                       │
│    Dashboard │ Risk Queue │ Order Detail │ Analytics     │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / REST
┌──────────────────────▼──────────────────────────────────┐
│                    FASTAPI BACKEND                        │
│   /health  /risk/score  /risk/{id}  /dashboard/summary   │
│   /metrics  /model/info  /review/{id}                    │
└──────┬──────────┬──────────┬──────────┬─────────────────┘
       │          │          │          │
┌──────▼───┐ ┌───▼─────┐ ┌─▼────────┐ ┌▼────────────────┐
│ Risk     │ │ ML      │ │ Business │ │ Explainability   │
│ Engine   │ │ Model   │ │ Cost     │ │ Engine (SHAP)    │
│          │ │         │ │ Engine   │ │                  │
└──────────┘ └─────────┘ └──────────┘ └──────────────────┘
       │          │          │          │
┌──────▼──────────▼──────────▼──────────▼─────────────────┐
│                     DATABASE (SQLite)                     │
│   customers │ products │ orders │ predictions │ reviews   │
└─────────────────────────────────────────────────────────┘
```

## 2. Inference Pipeline (Production Path)

This is the flow for scoring a new order:

```
New Order (JSON)
       │
       ▼
┌─────────────────┐
│ Input Validation │  ← Pydantic schemas
└────────┬────────┘
         ▼
┌─────────────────┐
│ Feature Pipeline │  ← Extract pre-fulfillment features
│                  │  ← Join with customer/product history
└────────┬────────┘
         ▼
┌─────────────────┐
│   ML Model      │  ← Trained classifier (XGBoost/LightGBM)
│   Inference      │  ← Output: calibrated probability
└────────┬────────┘
         ▼
┌─────────────────┐
│  Risk Engine     │  ← Apply optimized threshold
│                  │  ← Map probability → risk level
│                  │  ← Map risk level → recommended action
└────────┬────────┘
         ▼
┌─────────────────┐
│  Explainability  │  ← SHAP values for top features
│  Engine          │  ← Human-readable risk factor descriptions
└────────┬────────┘
         ▼
┌─────────────────┐
│  Business Cost   │  ← Estimate potential return cost
│  Engine          │  ← Calculate expected loss
└────────┬────────┘
         ▼
┌─────────────────┐
│  Response        │  ← Assemble final risk assessment
│  Assembly        │  ← Store prediction in database
└────────┬────────┘
         ▼
   Risk Assessment JSON
```

## 3. Training Pipeline (Offline Path)

```
Raw Dataset
       │
       ▼
┌─────────────────┐
│ Data Validation  │  ← Schema checks, range checks, integrity
└────────┬────────┘
         ▼
┌─────────────────┐
│ Preprocessing    │  ← Clean, encode, impute
└────────┬────────┘
         ▼
┌─────────────────┐
│ Feature Engg.    │  ← Engineer pre-fulfillment features
│                  │  ← Leakage audit: remove post-fulfillment
└────────┬────────┘
         ▼
┌─────────────────┐
│ Train/Val/Test   │  ← 70/15/15 stratified split
│ Split            │  ← Test set locked until Phase 16
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼ (locked)
┌────────┐ ┌──────┐
│Train+Val│ │ Test │
└───┬────┘ └──────┘
    ▼
┌─────────────────┐
│ Baseline Model   │  ← Logistic Regression
└────────┬────────┘
         ▼
┌─────────────────┐
│ Advanced Models  │  ← XGBoost, LightGBM, Random Forest
│ (on validation)  │  ← Compare metrics, select best
└────────┬────────┘
         ▼
┌─────────────────┐
│ Probability      │  ← Calibration curves
│ Calibration      │  ← Platt scaling / isotonic if needed
└────────┬────────┘
         ▼
┌─────────────────┐
│ Threshold        │  ← Sweep thresholds (0.1 – 0.9)
│ Optimization     │  ← Business cost optimization
│                  │  ← Select operating threshold
└────────┬────────┘
         ▼
┌─────────────────┐
│ Final Test       │  ← ONE-TIME evaluation on held-out test
│ Evaluation       │  ← Report all metrics
└─────────────────┘
```

## 4. Component Architecture

### 4.1 Data Layer (`src/data/`)

| Module | Responsibility |
|--------|---------------|
| `download_dataset.py` | Reproducible dataset acquisition |
| `inspect_dataset.py` | Initial data profiling |
| `validate_dataset.py` | Schema and integrity validation |
| `preprocess.py` | Cleaning, encoding, imputation |
| `features.py` | Feature engineering (pre-fulfillment only) |

### 4.2 ML Layer (`src/ml/`)

| Module | Responsibility |
|--------|---------------|
| `split.py` | Train/validation/test splitting with leakage checks |
| `train_baseline.py` | Logistic Regression baseline |
| `train_advanced.py` | XGBoost / LightGBM training |
| `evaluate.py` | Metrics computation and reporting |
| `predict.py` | Inference from trained model |
| `calibrate.py` | Probability calibration |
| `threshold.py` | Threshold optimization |

### 4.3 Business Layer (`src/business/`)

| Module | Responsibility |
|--------|---------------|
| `cost_engine.py` | Configurable cost model for FP/FN |

### 4.4 Explainability Layer (`src/explainability/`)

| Module | Responsibility |
|--------|---------------|
| `explainer.py` | SHAP-based feature importance and explanations |

### 4.5 Risk Engine (`src/risk/`)

| Module | Responsibility |
|--------|---------------|
| `engine.py` | Probability → risk level → action mapping |

### 4.6 Backend (`src/backend/`)

| Module | Responsibility |
|--------|---------------|
| `main.py` | FastAPI application |
| `routes/` | API endpoint handlers |
| `schemas.py` | Pydantic request/response models |
| `database.py` | SQLAlchemy models and session management |

### 4.7 Frontend (`src/frontend/`)

| Component | Responsibility |
|-----------|---------------|
| Dashboard | Summary statistics and risk overview |
| RiskQueue | Table of flagged orders with filters |
| OrderDetail | Full risk assessment for a single order |
| Analytics | Charts: distributions, trends, thresholds |
| ModelPerformance | ML metrics display |

## 5. Database Schema (SQLite)

```sql
-- Core tables
customers    (customer_id PK, segment, created_at, ...)
products     (product_id PK, category, price, ...)
orders       (order_id PK, customer_id FK, product_id FK, order_value, ...)

-- Risk assessment tables
risk_predictions (
    prediction_id PK,
    order_id FK,
    return_probability REAL,
    risk_level TEXT,        -- LOW | MEDIUM | HIGH
    recommended_action TEXT, -- APPROVE | MANUAL_REVIEW | HOLD
    risk_factors JSON,
    estimated_return_cost REAL,
    model_version TEXT,
    created_at TIMESTAMP
)

risk_reviews (
    review_id PK,
    prediction_id FK,
    order_id FK,
    model_recommendation TEXT,
    human_decision TEXT,     -- APPROVE | HOLD | REQUEST_REVIEW | MARK_FALSE_POSITIVE
    review_reason TEXT,
    reviewed_by TEXT,
    reviewed_at TIMESTAMP
)

model_versions (
    version_id PK,
    model_name TEXT,
    model_version TEXT,
    training_date TIMESTAMP,
    metrics JSON,
    threshold REAL,
    is_active BOOLEAN
)
```

## 6. API Design

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check |
| `POST` | `/api/v1/risk/score` | Score a new order |
| `GET` | `/api/v1/risk/{order_id}` | Get risk assessment for order |
| `GET` | `/api/v1/risk` | List all risk assessments (paginated) |
| `GET` | `/api/v1/dashboard/summary` | Dashboard summary stats |
| `GET` | `/api/v1/metrics` | Model performance metrics |
| `GET` | `/api/v1/model/info` | Active model metadata |
| `POST` | `/api/v1/review/{order_id}` | Submit human review decision |

## 7. Security Architecture

- **Input validation**: Pydantic models on all endpoints
- **CORS**: Configured for known origins only
- **Secrets**: `.env` file, never committed (`.env.example` template provided)
- **SQL injection**: SQLAlchemy ORM (parameterized queries)
- **Logging**: Structured logging, no sensitive data in logs
- **Error handling**: Generic error messages to clients, detailed logs internally
- **Data minimization**: No unnecessary PII stored

## 8. Deployment Architecture

```
┌──────────────────────────────────────────┐
│           docker-compose                  │
│                                          │
│  ┌────────────────┐  ┌────────────────┐  │
│  │  backend        │  │  frontend       │  │
│  │  (FastAPI +     │  │  (Nginx +       │  │
│  │   Uvicorn)      │  │   React build)  │  │
│  │  Port 8000      │  │  Port 3000      │  │
│  └───────┬────────┘  └────────────────┘  │
│          │                                │
│  ┌───────▼────────┐                      │
│  │  SQLite DB      │                      │
│  │  (volume mount) │                      │
│  └────────────────┘                      │
└──────────────────────────────────────────┘
```
