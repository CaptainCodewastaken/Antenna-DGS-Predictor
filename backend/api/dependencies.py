"""
API Dependencies.
Loads the model registry on startup and makes it available to routes.
"""
from backend.ml_models.registry import ModelRegistry

_registry = None

def load_models(models_dir: str = "backend/data/models") -> None:
    global _registry
    _registry = ModelRegistry(models_dir)

def get_registry() -> ModelRegistry:
    if _registry is None:
        raise RuntimeError("Model registry not initialized.")
    return _registry
