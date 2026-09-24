"""Health check endpoint."""
from fastapi import APIRouter, Depends
from backend.api.dependencies import get_registry, ModelRegistry

router = APIRouter()

@router.get("/health")
def health_check(registry: ModelRegistry = Depends(get_registry)):
    return {
        "status": "ok",
        "models_loaded": len(registry.models)
    }
