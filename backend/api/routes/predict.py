"""Predict endpoint."""
from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool

from backend.api.schemas import PredictRequest, PredictResponse
from backend.api.dependencies import get_registry, ModelRegistry
from backend.physics_engine import calculate_antenna_metrics
from backend.physics_engine.types import AntennaConfig, SubstrateConfig, PatchConfig, FeedConfig, DGSSlot

router = APIRouter()

@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest, registry: ModelRegistry = Depends(get_registry)):
    # Convert Pydantic request to physics Engine objects
    config = AntennaConfig(
        substrate=SubstrateConfig(**request.substrate.model_dump()),
        patch=PatchConfig(**request.patch.model_dump()),
        feed=FeedConfig(**request.feed.model_dump()),
        slots=[DGSSlot(**s.model_dump()) for s in request.slots]
    )
    
    # Physics prediction
    phys_metrics = await run_in_threadpool(calculate_antenna_metrics, config)
    
    # ML features construction (same logic as generate.py flatten_config)
    features = {
        "sub_eps_r": config.substrate.epsilon_r,
        "sub_tan_d": config.substrate.tan_delta,
        "sub_h": config.substrate.height_mm,
        "sub_size": config.substrate.width_mm,
        "patch_l": config.patch.length_mm,
        "patch_w": config.patch.width_mm,
        "feed_w": config.feed.width_mm,
        "feed_inset": config.feed.inset_mm,
        "num_slots": len(config.slots),
    }

    # Pad slots to exactly 2 for the ML model input
    for i in range(2):
        s = config.slots[i] if i < len(config.slots) else None
        prefix = f"slot{i+1}_"
        features.update({
            f"{prefix}l": s.length_mm if s else 0.0,
            f"{prefix}w": s.width_mm if s else 0.0,
            f"{prefix}x": s.x_mm if s else 0.0,
            f"{prefix}y": s.y_mm if s else 0.0
        })
        
    # ML Prediction
    ml_preds = await run_in_threadpool(registry.predict_all, features)
    
    return PredictResponse(
        physics=phys_metrics,
        ml_predictions=ml_preds
    )
