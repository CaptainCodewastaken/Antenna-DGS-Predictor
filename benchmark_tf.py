import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import tensorflow as tf
tf.config.set_visible_devices([], 'GPU')
import pandas as pd
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

def calculate_metrics(y_true, y_pred):
    return mean_absolute_error(y_true, y_pred), root_mean_squared_error(y_true, y_pred), r2_score(y_true, y_pred)

df = pd.read_csv('antenna_data.csv')
feature_cols = ['Sub_W', 'Sub_L', 'Sub_H', 'Patch_W', 'Patch_L', 'Feed_W', 'Slot1_W', 'Slot1_L', 'Slot2_W', 'Slot2_L']
target_cols = ['Freq_GHz', 'Gain']

X = df[feature_cols].values
y = df[target_cols].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler_X = StandardScaler()
X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)

X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))

model = Sequential([
    LSTM(64, activation='relu', input_shape=(1, 10)),
    Dense(32, activation='relu'),
    Dense(2)
])
model.compile(optimizer='adam', loss='mse')
model.fit(X_train_lstm, y_train, epochs=50, batch_size=32, verbose=0)
preds = model.predict(X_test_lstm, verbose=0)

out = {"LSTM Network": {"MAE": round(mean_absolute_error(y_test, preds),4), 
                        "RMSE": round(root_mean_squared_error(y_test, preds),4), 
                        "R2": round(r2_score(y_test, preds),4)}}
print(json.dumps(out))
