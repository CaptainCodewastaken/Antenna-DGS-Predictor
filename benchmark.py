import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import tensorflow as tf
tf.config.set_visible_devices([], 'GPU')
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

def calculate_metrics(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = root_mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return mae, rmse, r2

def main():
    # 1. Load Data
    df = pd.read_csv('antenna_data.csv')
    
    feature_cols = ['Sub_W', 'Sub_L', 'Sub_H', 'Patch_W', 'Patch_L', 'Feed_W', 'Slot1_W', 'Slot1_L', 'Slot2_W', 'Slot2_L']
    target_cols = ['Freq_GHz', 'Gain']
    
    X = df[feature_cols].values
    y = df[target_cols].values
    
    # 2. Preprocessing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler_X = StandardScaler()
    X_train_scaled = scaler_X.fit_transform(X_train)
    X_test_scaled = scaler_X.transform(X_test)
    
    # To keep targets at natural scale, we don't scale y for trees, but we will for LSTM later if needed.
    # Actually, let's keep y unscaled so metrics are easy to interpret.
    
    results = {}
    
    # --- Model 1: Linear Regression ---
    print("Training Linear Regression...")
    lr_model = LinearRegression()
    lr_model.fit(X_train_scaled, y_train)
    lr_preds = lr_model.predict(X_test_scaled)
    results['Linear Regression'] = calculate_metrics(y_test, lr_preds)
    
    # --- Model 2: K-Nearest Neighbors ---
    print("Training K-Nearest Neighbors...")
    knn_model = KNeighborsRegressor(n_neighbors=5)
    knn_model.fit(X_train_scaled, y_train)
    knn_preds = knn_model.predict(X_test_scaled)
    results['K-Nearest Neighbors'] = calculate_metrics(y_test, knn_preds)
    
    # --- Model 3: XGBoost ---
    print("Training XGBoost...")
    xgb_model = MultiOutputRegressor(XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42))
    xgb_model.fit(X_train_scaled, y_train)
    xgb_preds = xgb_model.predict(X_test_scaled)
    results['XGBoost'] = calculate_metrics(y_test, xgb_preds)
    
    # --- Model 4: LSTM ---
    print("Training LSTM...")
    # Reshape X for LSTM: [samples, time steps, features]
    # We will treat each sample as 1 time step with 10 features
    X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
    X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))
    
    lstm_model = Sequential()
    lstm_model.add(LSTM(64, activation='relu', input_shape=(1, 10)))
    lstm_model.add(Dense(32, activation='relu'))
    lstm_model.add(Dense(2)) # Predict 2 targets
    
    lstm_model.compile(optimizer='adam', loss='mse')
    lstm_model.fit(X_train_lstm, y_train, epochs=50, batch_size=32, verbose=0)
    
    lstm_preds = lstm_model.predict(X_test_lstm, verbose=0)
    results['LSTM Network'] = calculate_metrics(y_test, lstm_preds)
    
    # Format and save output
    formatted_results = {}
    for model_name, (mae, rmse, r2) in results.items():
        formatted_results[model_name] = {
            "MAE": round(mae, 4),
            "RMSE": round(rmse, 4),
            "R2": round(r2, 4)
        }
        
    print("\n--- BENCHMARK_RESULTS_JSON ---")
    print(json.dumps(formatted_results, indent=4))
    print("------------------------------\n")

if __name__ == '__main__':
    main()
