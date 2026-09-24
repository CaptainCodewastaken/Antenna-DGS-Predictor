import pandas as pd
from typing import Tuple, List

def load_and_preprocess_data(filepath: str) -> pd.DataFrame:
    """
    Loads the dataset and drops nulls.
    Vectorized pandas operations are used to adhere to project guidelines.
    """
    df = pd.read_csv(filepath)
    df = df.dropna()
    # Assuming standard column names. If different, we'll map them in main.py
    return df

def get_forward_data(df: pd.DataFrame, feature_cols: List[str], target_col: str) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Splits data for Forward Performance Prediction.
    X: Physical dimensions
    y: Performance metric (e.g., Operating Frequency or S11)
    """
    X = df[feature_cols]
    y = df[target_col]
    return X, y

def get_inverse_data(df: pd.DataFrame, feature_cols: List[str], target_cols: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits data for Inverse Antenna Design.
    X: Performance metrics (e.g., Operating Frequency, Gain)
    y: Physical dimensions
    """
    X = df[feature_cols]
    y = df[target_cols]
    return X, y
