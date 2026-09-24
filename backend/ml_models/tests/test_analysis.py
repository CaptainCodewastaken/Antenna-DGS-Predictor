"""Tests for analysis pipeline."""
import os
import json
import tempfile

from backend.data_generator.generate import generate_dataset
from backend.ml_models.analysis import run_analysis

def test_run_analysis() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Generate tiny dataset
        csv_path = os.path.join(tmpdir, "test.csv")
        generate_dataset(n_samples=50, seed=42, output_path=csv_path)
        
        # Analyze
        analysis_dir = os.path.join(tmpdir, "analysis")
        run_analysis(csv_path, analysis_dir)
        
        fi_path = os.path.join(analysis_dir, "feature_importance.json")
        lc_path = os.path.join(analysis_dir, "learning_curves.json")
        
        assert os.path.exists(fi_path)
        assert os.path.exists(lc_path)
        
        with open(fi_path, "r") as f:
            fi = json.load(f)
            
        assert "xgboost" in fi
        assert "linear" in fi
        
        # Patch_l should exist
        assert "patch_l" in fi["xgboost"]["resonant_frequency_hz"]
        
        with open(lc_path, "r") as f:
            lc = json.load(f)
            
        assert "xgboost" in lc
        assert "train_sizes" in lc["xgboost"]["resonant_frequency_hz"]
