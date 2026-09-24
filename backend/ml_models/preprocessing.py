"""
Preprocessing pipeline for the antenna ML models.
Handles feature scaling, train/test splitting, and feature extraction.
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from typing import Tuple

# The exact 18 features used to train the models
FEATURES = [
    "sub_eps_r", "sub_tan_d", "sub_h", "sub_size",
    "patch_l", "patch_w", "feed_w", "feed_inset",
    "num_slots", 
    "slot1_l", "slot1_w", "slot1_x", "slot1_y",
    "slot2_l", "slot2_w", "slot2_x", "slot2_y"
]

# We are predicting all 4 metrics
TARGETS = [
    "resonant_frequency_hz",
    "gain_dbi",
    "impedance_ohms",
    "bandwidth_fractional"
]

def load_and_preprocess(csv_path: str, test_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, StandardScaler]:
    """
    Load data from CSV, split into train and test, and fit a StandardScaler.

    Returns:
        X_train, X_test, y_train, y_test, scaler
    """
    df = pd.read_csv(csv_path)
    
    X = df[FEATURES]
    y = df[TARGETS]
    
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    scaler = StandardScaler()
    X_train = pd.DataFrame(scaler.fit_transform(X_train_raw), columns=FEATURES, index=X_train_raw.index)
    X_test = pd.DataFrame(scaler.transform(X_test_raw), columns=FEATURES, index=X_test_raw.index)
    
    return X_train, X_test, y_train, y_test, scaler


def preprocess_single(features_dict: dict, scaler: StandardScaler) -> pd.DataFrame:
    """Preprocess a single sample for inference."""
    # Ensure columns are exactly in the order of FEATURES
    row = pd.DataFrame([features_dict])[FEATURES]
    scaled = scaler.transform(row)
    return pd.DataFrame(scaled, columns=FEATURES)
