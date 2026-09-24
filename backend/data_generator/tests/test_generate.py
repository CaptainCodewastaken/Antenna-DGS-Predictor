"""Tests for the dataset generator."""
import os
import tempfile
import pandas as pd

from backend.data_generator.generate import generate_dataset

def test_generate_dataset_outputs_files() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "test.csv")
        parquet_path = os.path.join(tmpdir, "test.parquet")
        
        generate_dataset(n_samples=50, seed=42, output_path=csv_path)
        
        assert os.path.exists(csv_path)
        assert os.path.exists(parquet_path)
        
        df = pd.read_csv(csv_path)
        assert len(df) == 50
        
        # Check expected columns
        expected_cols = [
            "sub_eps_r", "sub_tan_d", "sub_h",
            "patch_l", "patch_w", "feed_w", "feed_inset",
            "num_slots", 
            "slot1_l", "slot1_w", "slot1_x", "slot1_y",
            "slot2_l", "slot2_w", "slot2_x", "slot2_y",
            "resonant_frequency_hz", "gain_dbi", "impedance_ohms", "bandwidth_fractional"
        ]
        
        for col in expected_cols:
            assert col in df.columns
            
        # Ensure no NaNs
        assert not df.isnull().values.any()
