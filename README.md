# ReturnGuard AI

> **Predict return risk before fulfillment, and help merchants make cost-aware decisions.**

[![Track](https://img.shields.io/badge/Razorpay%20Buildathon-Track%2002%20AI%20Risk%20Manager-blue)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()
[![Python](https://img.shields.io/badge/Python-3.10+-blue)]()
[![React](https://img.shields.io/badge/React-18+-61DAFB)]()

---

## Problem

E-commerce and D2C merchants lose significant revenue to product returns. Most systems only react **after** a return happens — by then the shipping, handling, and margin loss have already occurred.

**ReturnGuard AI** predicts the probability that an order will be returned **before fulfillment**, enabling merchants to make informed, cost-aware decisions about how to process each order.

## Solution

ReturnGuard is a **decision-support system** (not an auto-reject system) that:

1. **Predicts** return probability for each order before fulfillment
2. **Classifies** orders into LOW / MEDIUM / HIGH risk levels
3. **Explains** the major factors driving the risk score
4. **Estimates** the potential business cost of returns vs. false flags
5. **Recommends** an operational action (Approve / Manual Review / Hold)
6. **Enables** human analysts to override recommendations
7. **Records** outcomes for continuous improvement
8. **Provides** analytics and ML performance dashboards

## Responsible AI

> **ReturnGuard predicts return risk based on historical patterns. It does not determine customer intent or establish wrongdoing.**

- This is a **defensive-only** financial risk system
- The system **never** labels customers as fraudsters
- All predictions are probability estimates, not determinations of guilt
- Human oversight is built into every decision flow
- Language uses risk-appropriate terms: "high return risk", "requires review", "risk indicators detected"

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React, TypeScript, Vite, Tailwind CSS, Recharts |
| **Backend** | Python, FastAPI, Pydantic, Uvicorn |
| **ML** | pandas, numpy, scikit-learn, XGBoost/LightGBM, SHAP |
| **Database** | SQLite, SQLAlchemy |
| **Testing** | pytest, Vitest |
| **Deployment** | Docker, docker-compose |

## Project Structure

```
ReturnGuard/
├── data/                    # Datasets (raw, processed, splits)
│   ├── raw/
│   ├── processed/
│   └── splits/
├── docs/                    # Documentation
│   ├── architecture.md
│   ├── project-requirements.md
│   ├── development-plan.md
│   ├── ml-strategy.md
│   └── business-metrics.md
├── models/                  # Trained model artifacts
├── reports/                 # Generated analysis reports
├── src/                     # Source code
│   ├── backend/             # FastAPI application
│   ├── business/            # Business cost engine
│   ├── data/                # Data loading, validation, feature engineering
│   ├── explainability/      # SHAP / model explanation
│   ├── frontend/            # React dashboard
│   └── ml/                  # ML training, evaluation, prediction
├── tests/                   # Test suites
│   ├── backend/
│   ├── ml/
│   └── frontend/
├── .env.example             # Environment variable template
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Container definition
└── README.md                # This file
```

## Quick Start

> ⚠️ **Phase 0 — Architecture Only.** Full setup instructions will be added as phases are completed.

```bash
# Clone the repository
git clone <repo-url>
cd ReturnGuard

# Copy environment template
cp .env.example .env

# Backend setup (Python 3.10+)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Frontend setup (Node.js 18+)
cd src/frontend
npm install
npm run dev
```

## Dataset

The project uses publicly available data for demonstration and research purposes. See [docs/dataset-selection.md](docs/dataset-selection.md) for details on dataset sourcing and evaluation.

> **Note:** This project does NOT use actual Razorpay data. All data is either public or synthetically generated.

## Current Phase

**Phase 0 — Project Discovery and Architecture** ✅

## License

MIT
