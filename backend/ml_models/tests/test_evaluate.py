"""Tests for evaluation pipeline."""
import os
import json
import tempfile
import pandas as pd

from backend.data_generator.generate import generate_dataset
from backend.ml_models.evaluate import evaluate_models

def test_evaluate_models() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Generate tiny dataset
        csv_path = os.path.join(tmpdir, "test.csv")
        generate_dataset(n_samples=50, seed=42, output_path=csv_path)
        
        # Evaluate
        analysis_dir = os.path.join(tmpdir, "analysis")
        evaluate_models(csv_path, analysis_dir)
        
        metrics_path = os.path.join(analysis_dir, "metrics.json")
        cv_path = os.path.join(analysis_dir, "cross_validation.json")
        
        assert os.path.exists(metrics_path)
        assert os.path.exists(cv_path)
        
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
            
        assert "xgboost" in metrics
        assert "linear" in metrics
        
        # Check targets
        assert "resonant_frequency_hz" in metrics["xgboost"]
        assert "gain_dbi" in metrics["xgboost"]
        
        # Check metric keys
        assert "r2" in metrics["xgboost"]["resonant_frequency_hz"]
        assert "mae" in metrics["xgboost"]["resonant_frequency_hz"]
        
        with open(cv_path, "r") as f:
            cv = json.load(f)
            
        # 5 folds
        assert len(cv["xgboost"]["resonant_frequency_hz"]["r2"]) == 5
