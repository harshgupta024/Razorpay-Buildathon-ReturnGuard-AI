"""
ReturnGuard AI — Configuration & Policy Strategy Endpoints (/api/v1/config)
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.backend.routes.api_score import get_scoring_engine
from src.backend.schemas import ThresholdPresetResponse
from src.risk.scoring_engine import RiskScoringEngine
from src.risk.thresholds import MERCHANT_STRATEGY_PRESETS, RiskTierConfig

router = APIRouter(prefix="/api/v1/config", tags=["Configuration & Strategy Presets"])

_active_preset_name = "Balanced (Default Cost-Optimal)"


class UpdatePresetRequest(BaseModel):
    preset_name: str = Field(..., description="Preset name to activate")


@router.get("/thresholds", response_model=ThresholdPresetResponse, status_code=status.HTTP_200_OK)
def get_threshold_config(engine: RiskScoringEngine = Depends(get_scoring_engine)):
    """Retrieve current active risk tier boundaries and all available strategy presets."""
    tier_cfg = engine.tier_config
    preset_details = {}
    for name, p in MERCHANT_STRATEGY_PRESETS.items():
        preset_details[name] = {
            "description": p["description"],
            "cutoffs": {
                "low": p["tier_config"].low_cutoff,
                "medium": p["tier_config"].medium_cutoff,
                "high": p["tier_config"].high_cutoff,
            },
            "cost_params": {
                "cost_fn_return_inr": p["cost_params"].cost_fn_return,
                "cost_fp_friction_inr": p["cost_params"].cost_fp_friction,
            },
        }

    return ThresholdPresetResponse(
        active_preset=_active_preset_name,
        active_cutoffs={
            "low": tier_cfg.low_cutoff,
            "medium": tier_cfg.medium_cutoff,
            "high": tier_cfg.high_cutoff,
        },
        available_presets=preset_details,
    )


@router.post("/thresholds", status_code=status.HTTP_200_OK)
def update_threshold_preset(
    payload: UpdatePresetRequest,
    engine: RiskScoringEngine = Depends(get_scoring_engine),
):
    """Switch active merchant risk strategy preset dynamically."""
    global _active_preset_name

    matched_preset = None
    for name, p in MERCHANT_STRATEGY_PRESETS.items():
        if payload.preset_name.lower() in name.lower():
            matched_preset = (name, p)
            break

    if not matched_preset:
        raise HTTPException(
            status_code=400,
            detail=f"Preset '{payload.preset_name}' not recognized. Available: {list(MERCHANT_STRATEGY_PRESETS.keys())}",
        )

    _active_preset_name = matched_preset[0]
    engine.tier_config = matched_preset[1]["tier_config"]

    return {
        "message": f"Successfully activated strategy preset '{_active_preset_name}'",
        "active_preset": _active_preset_name,
        "new_cutoffs": {
            "low": engine.tier_config.low_cutoff,
            "medium": engine.tier_config.medium_cutoff,
            "high": engine.tier_config.high_cutoff,
        },
    }
