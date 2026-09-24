"""
Evaluation Pipeline.

Computes comprehensive performance metrics for all models using
5-fold cross validation. Saves results to JSON.
"""
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, max_error
from sklearn.preprocessing import StandardScaler

from backend.ml_models.preprocessing import load_and_preprocess, FEATURES, TARGETS
from backend.ml_models.train import get_models

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


def mean_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate MAPE ignoring divide-by-zero."""
    # Prevent division by zero
    mask = y_true != 0
    if not np.any(mask):
        return 0.0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask]))


def evaluate_models(dataset_path: str, output_dir: str) -> None:
    """Run 5-fold CV on all models and save metrics."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Loading data from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    X_full = df[FEATURES].values
    y_full = df[TARGETS].values
    
    models = get_models()
    
    cv_results = {model_name: {target: {"r2": [], "mae": [], "rmse": [], "mape": [], "max_error": []} for target in TARGETS} for model_name in models}
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    for fold, (train_idx, test_idx) in enumerate(kf.split(X_full)):
        logger.info(f"--- Running Fold {fold + 1}/5 ---")
        X_tr, X_te = X_full[train_idx], X_full[test_idx]
        y_tr, y_te = y_full[train_idx], y_full[test_idx]
        
        # Scale features
        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X_tr)
        X_te = scaler.transform(X_te)
        
        for name, model in models.items():
            logger.info(f"  Training {name}...")
            model.fit(X_tr, y_tr)
            preds = model.predict(X_te)
            
            for t_idx, target in enumerate(TARGETS):
                y_true = y_te[:, t_idx]
                y_pred = preds[:, t_idx]
                
                r2 = r2_score(y_true, y_pred)
                mae = mean_absolute_error(y_true, y_pred)
                rmse = np.sqrt(mean_squared_error(y_true, y_pred))
                mape = mean_absolute_percentage_error(y_true, y_pred)
                me = max_error(y_true, y_pred)
                
                cv_results[name][target]["r2"].append(r2)
                cv_results[name][target]["mae"].append(mae)
                cv_results[name][target]["rmse"].append(rmse)
                cv_results[name][target]["mape"].append(mape)
                cv_results[name][target]["max_error"].append(me)

    # Aggregate results
    aggregated = {}
    for name, targets in cv_results.items():
        aggregated[name] = {}
        for target, metrics in targets.items():
            aggregated[name][target] = {
                "r2": float(np.mean(metrics["r2"])),
                "r2_std": float(np.std(metrics["r2"])),
                "mae": float(np.mean(metrics["mae"])),
                "rmse": float(np.mean(metrics["rmse"])),
                "mape": float(np.mean(metrics["mape"])),
                "max_error": float(np.max(metrics["max_error"])),
            }
            
    # Save results
    metrics_path = out_path / "metrics.json"
    cv_path = out_path / "cross_validation.json"
    
    with open(metrics_path, "w") as f:
        json.dump(aggregated, f, indent=2)
        
    with open(cv_path, "w") as f:
        json.dump(cv_results, f, indent=2)
        
    logger.info(f"Evaluation complete. Results saved to {out_path}.")
    
    # Print a quick summary for resonant_frequency_hz
    logger.info("Summary (Resonant Frequency R²):")
    for name in aggregated:
        logger.info(f"  {name}: {aggregated[name]['resonant_frequency_hz']['r2']:.4f}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate ML models")
    parser.add_argument("--dataset", type=str, required=True, help="Path to input dataset (CSV)")
    parser.add_argument("--output", type=str, default="backend/data/analysis", help="Output directory for analysis")
    
    args = parser.parse_args()
    evaluate_models(args.dataset, args.output)

if __name__ == "__main__":
    main()
