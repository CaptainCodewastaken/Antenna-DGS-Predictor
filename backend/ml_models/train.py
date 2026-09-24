"""
Training Pipeline.

Trains 8 machine learning models to predict the 4 antenna targets.
Saves the trained models and the scaler to disk.
"""
import argparse
import logging
import os
import json
from datetime import datetime
from pathlib import Path

import joblib
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.multioutput import MultiOutputRegressor
import xgboost as xgb

from backend.ml_models.preprocessing import load_and_preprocess

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


def get_models() -> dict:
    """Instantiate the 8 required models."""
    return {
        "linear": LinearRegression(),
        "ridge": Ridge(alpha=1.0),
        "lasso": Lasso(alpha=0.1),
        "knn": KNeighborsRegressor(n_neighbors=5),
        "decision_tree": DecisionTreeRegressor(random_state=42),
        "random_forest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        # XGBoost handles multi-output in recent versions, but MultiOutputRegressor is safer across versions
        "xgboost": MultiOutputRegressor(xgb.XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1)),
        "svr": MultiOutputRegressor(SVR(C=1.0, epsilon=0.1)),
    }


def train_models(dataset_path: str, output_dir: str) -> None:
    """Train all models and save them."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Loading and preprocessing data from {dataset_path}...")
    X_train, X_test, y_train, y_test, scaler = load_and_preprocess(dataset_path)
    
    # Save the scaler
    scaler_path = out_path / "scaler.joblib"
    joblib.dump(scaler, scaler_path)
    logger.info(f"Saved scaler to {scaler_path}")
    
    models = get_models()
    
    metadata = {
        "trained_at": datetime.utcnow().isoformat(),
        "dataset_path": dataset_path,
        "n_train_samples": len(X_train),
        "n_test_samples": len(X_test),
        "models": list(models.keys())
    }
    
    for name, model in models.items():
        logger.info(f"Training {name}...")
        model.fit(X_train, y_train)
        
        # Save model
        model_path = out_path / f"{name}.joblib"
        joblib.dump(model, model_path)
        logger.info(f"Saved {name} to {model_path}")
        
    # Save metadata
    meta_path = out_path / "metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved metadata to {meta_path}")
    

def main() -> None:
    parser = argparse.ArgumentParser(description="Train ML models")
    parser.add_argument("--dataset", type=str, required=True, help="Path to input dataset (CSV)")
    parser.add_argument("--output", type=str, default="backend/data/models", help="Output directory for models")
    
    args = parser.parse_args()
    train_models(args.dataset, args.output)


if __name__ == "__main__":
    main()
