"""Tests for model registry."""
import os
import tempfile
import pandas as pd

from backend.data_generator.generate import generate_dataset
from backend.ml_models.train import train_models
from backend.ml_models.registry import ModelRegistry

def test_registry_load_and_predict() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Train first
        csv_path = os.path.join(tmpdir, "test.csv")
        generate_dataset(n_samples=50, seed=42, output_path=csv_path)
        
        models_dir = os.path.join(tmpdir, "models")
        train_models(csv_path, models_dir)
        
        # Test Registry
        registry = ModelRegistry(models_dir)
        
        assert len(registry.models) == 8
        assert registry.scaler is not None
        
        # Test predict
        features = {
            "sub_eps_r": 4.4, "sub_tan_d": 0.02, "sub_h": 1.6, "sub_size": 60.0,
            "patch_l": 29.0, "patch_w": 38.0, "feed_w": 3.0, "feed_inset": 8.0,
            "num_slots": 1, 
            "slot1_l": 15.0, "slot1_w": 5.0, "slot1_x": 0.0, "slot1_y": 10.0,
            "slot2_l": 0.0, "slot2_w": 0.0, "slot2_x": 0.0, "slot2_y": 0.0,
        }
        
        preds = registry.predict("linear", features)
        assert "resonant_frequency_hz" in preds
        assert "gain_dbi" in preds
        assert "impedance_ohms" in preds
        assert "bandwidth_fractional" in preds
        
        all_preds = registry.predict_all(features)
        assert "xgboost" in all_preds
        assert "linear" in all_preds
        assert all_preds["xgboost"]["gain_dbi"] != all_preds["linear"]["gain_dbi"]
