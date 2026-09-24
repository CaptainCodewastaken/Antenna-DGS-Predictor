"""Tests for training pipeline."""
import os
import tempfile
import pandas as pd

from backend.data_generator.generate import generate_dataset
from backend.ml_models.train import train_models

def test_train_pipeline() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Generate small dataset
        csv_path = os.path.join(tmpdir, "test.csv")
        generate_dataset(n_samples=50, seed=42, output_path=csv_path)
        
        # 2. Train models
        models_dir = os.path.join(tmpdir, "models")
        train_models(csv_path, models_dir)
        
        # 3. Check outputs
        assert os.path.exists(os.path.join(models_dir, "metadata.json"))
        assert os.path.exists(os.path.join(models_dir, "scaler.joblib"))
        
        # Check that a few models exist
        assert os.path.exists(os.path.join(models_dir, "linear.joblib"))
        assert os.path.exists(os.path.join(models_dir, "xgboost.joblib"))
