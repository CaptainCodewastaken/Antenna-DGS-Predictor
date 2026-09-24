"""Model analysis endpoints."""
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter()

ANALYSIS_DIR = Path("backend/data/analysis")

def load_json_or_404(path: Path):
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path.name}")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare")
def compare_models():
    """Returns aggregated metrics for all models."""
    return load_json_or_404(ANALYSIS_DIR / "metrics.json")

@router.get("/feature-importance")
def feature_importance():
    """Returns feature importance data."""
    return load_json_or_404(ANALYSIS_DIR / "feature_importance.json")

@router.get("/learning-curves")
def learning_curves():
    """Returns learning curve data."""
    return load_json_or_404(ANALYSIS_DIR / "learning_curves.json")

@router.get("/cross-validation")
def cross_validation():
    """Returns raw cross-validation fold scores."""
    return load_json_or_404(ANALYSIS_DIR / "cross_validation.json")
