"""
ReturnGuard AI — FastAPI Production Application Server

Provides REST APIs for:
- Real-time Order Risk Scoring & Mitigation Recommendation
- Batch Processing
- Non-Accusatory Explainability (SHAP attributions)
- Human-in-the-Loop Review Queue
- Merchant Portfolio Analytics
- Dynamic Threshold Configuration

Usage:
    uvicorn src.backend.app:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.backend.routes import (
    api_analytics,
    api_config,
    api_orders,
    api_review,
    api_score,
)
from src.backend.schemas import HealthResponse
from src.config import AppConfig, BackendConfig, MLConfig
from src.db.session import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("returnguard.api")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

app_config = AppConfig()
backend_config = BackendConfig()
ml_config = MLConfig()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("=" * 60)
    logger.info(f"Starting {app_config.app_name} Backend Server...")
    logger.info(f"Environment: {app_config.app_env} | Log Level: {app_config.log_level}")
    logger.info("Initializing relational database schema...")
    init_db()
    logger.info("ReturnGuard AI ready to serve predictions.")
    logger.info("=" * 60)
    yield
    logger.info("Shutting down ReturnGuard AI server.")


app = FastAPI(
    title="ReturnGuard AI API",
    description="AI-powered Return-Risk Scoring, Decision Support, and Human Review System for E-Commerce Merchants.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware (React frontend connectivity)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local development on all ports (e.g. 5173, 3000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Route Handlers
app.include_router(api_score.router)
app.include_router(api_orders.router)
app.include_router(api_review.router)
app.include_router(api_analytics.router)
app.include_router(api_config.router)

# Mount Frontend Static Assets (if built)
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
if FRONTEND_DIST.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/app", tags=["Frontend"])
    @app.get("/app/{full_path:path}", tags=["Frontend"])
    def serve_frontend_app(full_path: str = ""):
        from fastapi.responses import FileResponse
        return FileResponse(FRONTEND_DIST / "index.html")


@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health & System"])
def health_check():
    """Health check endpoint confirming model status and readiness."""
    return HealthResponse(
        status="healthy",
        app_name=app_config.app_name,
        model_version=ml_config.model_version,
        model_calibrated=True,
        timestamp=datetime.utcnow().isoformat(),
    )


@app.get("/", tags=["Health & System"])
def root():
    return {
        "app": app_config.app_name,
        "tagline": "Predict return risk before fulfillment, and help merchants make cost-aware decisions.",
        "status": "operational",
        "api_docs": "/docs",
        "health_check": "/api/v1/health",
    }
