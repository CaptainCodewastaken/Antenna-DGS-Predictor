import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

class InverseModel:
    def __init__(self):
        self.model = DecisionTreeRegressor(random_state=42)

    def train(self, X: pd.DataFrame, y: pd.DataFrame):
        logging.info("Training Inverse Model (Decision Tree for Multi-Output)...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        
        predictions = self.model.predict(X_test)
        
        # Calculate metrics for each output dimension (since it's multi-output)
        # We can just take the average over all targets for a single summary metric
        mae = mean_absolute_error(y_test, predictions)
        rmse = root_mean_squared_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        logging.info(f"Inverse Model Evaluation - Average MAE: {mae:.4f}, Average RMSE: {rmse:.4f}, Average R2: {r2:.4f}")
        return mae, rmse, r2

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        return self.model.predict(X)
