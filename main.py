import logging
import os
from data_processor import load_and_preprocess_data, get_forward_data, get_inverse_data
from forward_model import ForwardModel
from inverse_model import InverseModel
import warnings

# Suppress sklearn warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def main():
    dataset_path = 'antenna_data.csv'
    
    if not os.path.exists(dataset_path):
        logging.error(f"Dataset not found at {dataset_path}. Please download the Kaggle dataset and place it here.")
        return

    logging.info("--- Starting Antenna ML Pipeline ---")
    
    # 1. Load Data
    df = load_and_preprocess_data(dataset_path)
    logging.info(f"Loaded dataset with {len(df)} records.")
    
    # Expected columns based on the Mendeley dataset
    feature_cols = ['Sub_W', 'Sub_L', 'Sub_H', 'Patch_W', 'Patch_L', 'Feed_W', 'Slot1_W', 'Slot1_L', 'Slot2_W', 'Slot2_L']
    target_forward = ['Freq_GHz', 'Gain']
    target_inverse = ['Freq_GHz', 'Gain']
    
    # Check if columns exist
    for col in feature_cols + target_forward:
        if col not in df.columns:
            logging.error(f"Column '{col}' not found in dataset. Please rename your columns to match.")
            return

    # 2. Forward Performance Prediction (XGBoost)
    logging.info("\n--- Phase 1: Forward Prediction ---")
    X_fwd, y_fwd = get_forward_data(df, feature_cols, target_forward)
    fwd_model = ForwardModel()
    fwd_model.train(X_fwd, y_fwd)
    
    # 3. Inverse Antenna Design (Decision Tree Multi-Output)
    logging.info("\n--- Phase 2: Inverse Design ---")
    X_inv, y_inv = get_inverse_data(df, target_inverse, feature_cols)
    inv_model = InverseModel()
    inv_model.train(X_inv, y_inv)
    
    logging.info("\n--- Pipeline Completed Successfully ---")

if __name__ == "__main__":
    main()
