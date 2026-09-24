"""
Model Registry.

Provides a unified interface for loading trained models and running inference.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import joblib
import pandas as pd

from backend.ml_models.preprocessing import TARGETS, preprocess_single

logger = logging.getLogger(__name__)

class ModelRegistry:
    """Registry to manage and query the trained ML models."""
    
    def __init__(self, models_dir: str = "backend/data/models"):
        self.models_dir = Path(models_dir)
        self.scaler = None
        self.models = {}
        self.metadata = {}
        
        self.load_all()
        
    def load_all(self) -> None:
        """Load the scaler, metadata, and all available models from disk."""
        meta_path = self.models_dir / "metadata.json"
        if not meta_path.exists():
            logger.warning(f"No metadata found at {meta_path}. Models may not be trained.")
            return
            
        with open(meta_path, "r") as f:
            self.metadata = json.load(f)
            
        scaler_path = self.models_dir / "scaler.joblib"
        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
            
        for name in self.metadata.get("models", []):
            model_path = self.models_dir / f"{name}.joblib"
            if model_path.exists():
                self.models[name] = joblib.load(model_path)
                
        logger.info(f"Loaded {len(self.models)} models from {self.models_dir}")
        
    def predict(self, model_name: str, features: Dict[str, float]) -> Dict[str, float]:
        """
        Run inference using a specific model.
        
        Args:
            model_name: The name of the model to use (e.g., 'xgboost')
            features: Dictionary of the 18 required features.
            
        Returns:
            Dictionary mapping target names to predicted values.
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not loaded or does not exist.")
            
        if self.scaler is None:
            raise RuntimeError("Scaler not loaded.")
            
        # Preprocess
        X = preprocess_single(features, self.scaler)
        
        # Predict
        model = self.models[model_name]
        preds = model.predict(X)[0] # First and only row
        
        return {target: float(pred) for target, pred in zip(TARGETS, preds)}
        
    def predict_all(self, features: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Run inference using all available models."""
        results = {}
        for name in self.models.keys():
            results[name] = self.predict(name, features)
        return results
