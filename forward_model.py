import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

class ForwardModel:
    def __init__(self):
        self.model = MultiOutputRegressor(XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42))

    def train(self, X: pd.DataFrame, y: pd.Series):
        logging.info("Training Forward Model (XGBoost)...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        
        predictions = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        rmse = root_mean_squared_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        logging.info(f"Forward Model Evaluation - MAE: {mae:.4f}, RMSE: {rmse:.4f}, R2: {r2:.4f}")
        return mae, rmse, r2

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)
