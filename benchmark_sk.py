import pandas as pd
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

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

results = {}

lr = LinearRegression()
lr.fit(X_train_scaled, y_train)
results['Linear Regression'] = calculate_metrics(y_test, lr.predict(X_test_scaled))

knn = KNeighborsRegressor(n_neighbors=5)
knn.fit(X_train_scaled, y_train)
results['K-Nearest Neighbors'] = calculate_metrics(y_test, knn.predict(X_test_scaled))

xgb = MultiOutputRegressor(XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42))
xgb.fit(X_train_scaled, y_train)
results['XGBoost'] = calculate_metrics(y_test, xgb.predict(X_test_scaled))

out = {}
for k, v in results.items():
    out[k] = {"MAE": round(v[0],4), "RMSE": round(v[1],4), "R2": round(v[2],4)}
print(json.dumps(out))
