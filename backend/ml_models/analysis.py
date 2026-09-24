"""
Model Analysis.

Computes feature importance and learning curves.
"""
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd
from sklearn.model_selection import learning_curve
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler

from backend.ml_models.preprocessing import load_and_preprocess, FEATURES, TARGETS
from backend.ml_models.train import get_models

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


def compute_feature_importance(models: Dict[str, Any], output_path: Path) -> None:
    """Compute feature importance for each target across compatible models."""
    importance_data = {model_name: {target: {} for target in TARGETS} for model_name in models}
    
    for name, model in models.items():
        # Depending on if it's MultiOutputRegressor or native multi-output
        if hasattr(model, "estimators_"):
            # MultiOutputRegressor wraps estimators
            estimators = model.estimators_
            for i, target in enumerate(TARGETS):
                est = estimators[i]
                if hasattr(est, "feature_importances_"):
                    imp = est.feature_importances_
                    importance_data[name][target] = {f: float(val) for f, val in zip(FEATURES, imp)}
                elif hasattr(est, "coef_"):
                    # Coef is 1D for single target
                    imp = np.abs(est.coef_)
                    # Normalize
                    imp_sum = np.sum(imp)
                    if imp_sum > 0:
                        imp = imp / imp_sum
                    importance_data[name][target] = {f: float(val) for f, val in zip(FEATURES, imp)}
        else:
            # Native multi-output model
            if hasattr(model, "feature_importances_"):
                # Usually 1D array of importance across all targets for trees
                imp = model.feature_importances_
                for target in TARGETS:
                    importance_data[name][target] = {f: float(val) for f, val in zip(FEATURES, imp)}
            elif hasattr(model, "coef_"):
                # Coef is (n_targets, n_features)
                for i, target in enumerate(TARGETS):
                    imp = np.abs(model.coef_[i])
                    imp_sum = np.sum(imp)
                    if imp_sum > 0:
                        imp = imp / imp_sum
                    importance_data[name][target] = {f: float(val) for f, val in zip(FEATURES, imp)}

    with open(output_path, "w") as f:
        json.dump(importance_data, f, indent=2)


def compute_learning_curves(dataset_path: str, output_path: Path) -> None:
    """Compute learning curves for a representative model."""
    df = pd.read_csv(dataset_path)
    X = df[FEATURES].values
    y = df[TARGETS].values
    
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    
    # We will compute learning curves for XGBoost and Linear Regression
    models = {
        "linear": get_models()["linear"],
        "xgboost": get_models()["xgboost"]
    }
    
    curve_data = {}
    
    for name, model in models.items():
        curve_data[name] = {}
        # We compute learning curves for the first target to save time
        # Or we can compute for all. Let's do the first target (resonant frequency)
        y_single = y[:, [0]]
        
        train_sizes, train_scores, test_scores = learning_curve(
            estimator=model,
            X=X,
            y=y_single,
            train_sizes=np.linspace(0.1, 1.0, 10),
            cv=5,
            scoring="r2",
            n_jobs=-1,
            random_state=42
        )
        
        train_scores_mean = np.mean(train_scores, axis=1)
        test_scores_mean = np.mean(test_scores, axis=1)
        
        curve_data[name]["resonant_frequency_hz"] = {
            "train_sizes": [int(s) for s in train_sizes],
            "train_r2": [float(r) for r in train_scores_mean],
            "test_r2": [float(r) for r in test_scores_mean]
        }
        
    with open(output_path, "w") as f:
        json.dump(curve_data, f, indent=2)


def run_analysis(dataset_path: str, output_dir: str) -> None:
    """Run all analysis pipelines."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    # Need to train the models to get feature importances
    logger.info("Training models for feature importance analysis...")
    X_train, _, y_train, _, _ = load_and_preprocess(dataset_path)
    models = get_models()
    for name, model in models.items():
        model.fit(X_train, y_train)
        
    logger.info("Computing feature importances...")
    compute_feature_importance(models, out_path / "feature_importance.json")
    
    logger.info("Computing learning curves...")
    compute_learning_curves(dataset_path, out_path / "learning_curves.json")
    
    logger.info(f"Analysis complete. Results saved to {out_path}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze ML models")
    parser.add_argument("--dataset", type=str, required=True, help="Path to input dataset (CSV)")
    parser.add_argument("--output", type=str, default="backend/data/analysis", help="Output directory for analysis")
    
    args = parser.parse_args()
    run_analysis(args.dataset, args.output)


if __name__ == "__main__":
    main()
