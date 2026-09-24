from fastapi import APIRouter

from .predict import router as predict_router
from .health import router as health_router
from .pattern import router as pattern_router
from .s_parameter import router as s_parameter_router
from .models import router as models_router
from .dgs import router as dgs_router

router = APIRouter()
router.include_router(predict_router, tags=["predict"])
router.include_router(health_router, tags=["health"])
router.include_router(pattern_router, tags=["pattern"])
router.include_router(s_parameter_router, tags=["s_parameter"])
router.include_router(models_router, prefix="/models", tags=["models"])
router.include_router(dgs_router, prefix="/dgs", tags=["dgs"])
