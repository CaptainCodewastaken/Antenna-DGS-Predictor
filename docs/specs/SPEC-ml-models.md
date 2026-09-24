# Spec: ml-models

> **Module ID:** `ml-models`  
> **Capability Map:** [capability_map.md](file:///Users/himaghnaroy/.gemini/antigravity-ide/brain/b5b0a198-c758-41d8-a785-cb83ea463b44/capability_map.md)  
> **Depends on:** `data-generator` (for training data)  
> **Consumed by:** `api`

---

## Objective

Train, evaluate, and serialize 8 ML models on the physics-engine-generated dataset. Provide a unified interface for prediction, comparison, and analysis (feature importance, learning curves, cross-validation). The physics engine's analytical predictions serve as the "ground truth" baseline that all ML models are compared against.

### The 8 Models

| # | Model | Class | Library | Why Include |
|---|-------|-------|---------|-------------|
| 1 | **Linear Regression** | Linear | sklearn | Baseline. Interpretable coefficients show linear relationships between geometry and performance. |
| 2 | **Ridge Regression** | Regularized linear | sklearn | L2 regularization. Shows effect of regularization on a linear model. |
| 3 | **Lasso Regression** | Regularized linear | sklearn | L1 regularization. Automatic feature selection — which dimensions does the model discard? |
| 4 | **K-Nearest Neighbors** | Instance-based | sklearn | Non-parametric. Captures local patterns. Shows how distance-based approaches handle antenna data. |
| 5 | **Decision Tree** | Tree | sklearn | Fully interpretable. Can visualize splits. Shows which dimensions are split first. |
| 6 | **Random Forest** | Ensemble (bagging) | sklearn | Averages many trees. More robust than single Decision Tree. Natural feature importance. |
| 7 | **XGBoost** | Ensemble (boosting) | xgboost | Likely accuracy winner. Gradient boosting with regularization. |
| 8 | **SVR** | Kernel-based | sklearn | Different learning paradigm. Margin-based. Shows how kernel methods compare. |

### Prediction Targets

Each model predicts **two targets** simultaneously:
- **Resonant frequency** (GHz)
- **Gain** (dBi)

Models that don't natively support multi-output (XGBoost, SVR) are wrapped in `sklearn.multioutput.MultiOutputRegressor`.

---

## Tech Stack

- **Language:** Python 3.10+
- **Dependencies:** scikit-learn, xgboost, numpy, pandas, joblib, matplotlib (for plot generation)
- **Serialization:** joblib (`.joblib` files)

---

## Commands

```bash
# Train all models on the generated dataset
python -m backend.ml_models.train --data backend/data/antenna_dataset.csv --output backend/ml_models/saved_models/

# Train a specific model
python -m backend.ml_models.train --data backend/data/antenna_dataset.csv --model xgboost

# Evaluate all saved models
python -m backend.ml_models.evaluate --data backend/data/antenna_dataset.csv --models-dir backend/ml_models/saved_models/

# Generate learning curves (saved as JSON for frontend)
python -m backend.ml_models.learning_curves --data backend/data/antenna_dataset.csv --output backend/ml_models/analysis/

# Run tests
pytest backend/ml_models/tests/ -v
```

---

## Project Structure

```
backend/ml_models/
├── __init__.py
├── train.py              # Training pipeline (CLI entry point)
├── registry.py           # Model registry: name → class mapping, unified predict/compare interface
├── evaluate.py           # Evaluation pipeline: metrics, cross-validation
├── analysis.py           # Feature importance, learning curves, residual analysis
├── preprocessing.py      # Feature scaling, train/test split
├── saved_models/         # Serialized .joblib files
│   ├── linear_regression.joblib
│   ├── ridge.joblib
│   ├── lasso.joblib
│   ├── knn.joblib
│   ├── decision_tree.joblib
│   ├── random_forest.joblib
│   ├── xgboost.joblib
│   ├── svr.joblib
│   ├── scaler.joblib        # StandardScaler fitted on training data
│   └── metadata.json        # Training metadata: date, dataset hash, hyperparams
├── analysis/             # Pre-computed analysis results (JSON)
│   ├── metrics.json
│   ├── feature_importance.json
│   ├── learning_curves.json
│   └── cross_validation.json
└── tests/
    ├── test_registry.py
    ├── test_train.py
    ├── test_evaluate.py
    └── test_analysis.py
```

---

## Model Registry (`registry.py`)

The registry provides a unified interface so the API and comparison logic don't need to know about individual model classes:

```python
from dataclasses import dataclass
from typing import Protocol
import numpy as np

class PredictorProtocol(Protocol):
    def predict(self, X: np.ndarray) -> np.ndarray: ...

@dataclass
class ModelInfo:
    name: str                    # e.g., "XGBoost"
    slug: str                    # e.g., "xgboost" (used in filenames, API)
    category: str                # e.g., "Ensemble (Boosting)"
    description: str             # One-line description
    model: PredictorProtocol     # The fitted model
    metrics: dict                # {"freq_r2": 0.99, "gain_r2": 0.97, ...}

class ModelRegistry:
    """Manages all trained models with a unified interface."""

    def __init__(self, models_dir: str = "backend/ml_models/saved_models/"):
        self.models: dict[str, ModelInfo] = {}
        self._load_models(models_dir)

    def predict(self, model_slug: str, X: np.ndarray) -> dict:
        """Predict using a specific model. Returns {"freq_ghz": ..., "gain_dbi": ...}."""

    def predict_all(self, X: np.ndarray) -> dict[str, dict]:
        """Predict using all models. Returns {model_slug: {"freq_ghz": ..., "gain_dbi": ...}}."""

    def compare(self, X: np.ndarray, y_true: np.ndarray | None = None) -> dict:
        """Compare all models on the same input. Returns predictions + metrics."""

    def get_metrics(self) -> dict[str, dict]:
        """Return pre-computed metrics for all models."""

    def get_feature_importance(self) -> dict[str, list]:
        """Return feature importance for tree-based models."""

    def get_learning_curves(self) -> dict[str, dict]:
        """Return pre-computed learning curve data."""
```

---

## Training Pipeline (`train.py`)

### Data Preprocessing

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 1. Load dataset
df = pd.read_csv(data_path)

# 2. Feature columns (inputs)
FEATURE_COLS = [
    "Sub_W", "Sub_L", "Sub_H", "Epsilon_r", "Tan_delta",
    "Patch_W", "Patch_L", "Feed_W", "Feed_Inset",
    "Num_Slots", "Slot1_W", "Slot1_L", "Slot1_X", "Slot1_Y",
    "Slot2_W", "Slot2_L", "Slot2_X", "Slot2_Y",
]

# 3. Target columns (outputs)
TARGET_COLS = ["Freq_GHz", "Gain_dBi"]

# 4. Split: 80% train, 20% test (stratified by Num_Slots)
X_train, X_test, y_train, y_test = train_test_split(
    df[FEATURE_COLS], df[TARGET_COLS],
    test_size=0.2, random_state=42
)

# 5. Scale features (save scaler for inference)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

### Hyperparameters

| Model | Key Hyperparameters |
|-------|-------------------|
| Linear Regression | None (closed-form) |
| Ridge | `alpha=1.0` |
| Lasso | `alpha=0.01` |
| KNN | `n_neighbors=5, weights='distance', metric='minkowski'` |
| Decision Tree | `max_depth=15, min_samples_leaf=5` |
| Random Forest | `n_estimators=200, max_depth=20, min_samples_leaf=3` |
| XGBoost | `n_estimators=200, max_depth=8, learning_rate=0.1, reg_alpha=0.1, reg_lambda=1.0` |
| SVR | `kernel='rbf', C=100, epsilon=0.01` (wrapped in MultiOutputRegressor) |

> **Note:** These are starting points. No hyperparameter search in v1 — if time permits, add `GridSearchCV` or `Optuna` as a stretch goal.

### Training Output

Each model produces:
1. **Serialized model** → `saved_models/{slug}.joblib`
2. **Metrics on test set** → appended to `analysis/metrics.json`
3. **Training log** → console + log file

---

## Evaluation Metrics (`evaluate.py`)

### Per-Model Metrics

Computed separately for each target (frequency and gain):

```python
metrics = {
    "freq": {
        "r2": float,         # R² score
        "mae": float,        # Mean Absolute Error
        "rmse": float,       # Root Mean Squared Error
        "max_error": float,  # Maximum absolute error
        "mape": float,       # Mean Absolute Percentage Error
    },
    "gain": {
        # Same structure
    },
    "overall": {
        "r2": float,         # Average R² across both targets
        "training_time_s": float,
    }
}
```

### Cross-Validation

5-fold cross-validation for each model:
```python
from sklearn.model_selection import cross_val_score

cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="r2")
# Store: mean, std, per-fold scores
```

---

## Analysis (`analysis.py`)

### Feature Importance

For tree-based models (Decision Tree, Random Forest, XGBoost):
```python
importance = model.feature_importances_  # shape (n_features,)
# Map to feature names, sort descending
```

For linear models (Linear, Ridge, Lasso):
```python
coefficients = model.coef_  # shape (n_targets, n_features)
# Absolute values as "importance"
```

For Lasso specifically: report which features have zero coefficients (dropped by L1).

**Output format** (JSON, consumed by frontend):
```json
{
    "feature_names": ["Sub_W", "Sub_L", ...],
    "models": {
        "xgboost": {"freq": [0.05, 0.03, ...], "gain": [0.08, 0.02, ...]},
        "random_forest": {...},
        "lasso": {"zero_features": ["Feed_W", "Slot2_Y"]}
    }
}
```

### Learning Curves

Train each model on increasing fractions of the training set (10%, 20%, ..., 100%) and record test R²:

```python
from sklearn.model_selection import learning_curve

train_sizes, train_scores, test_scores = learning_curve(
    model, X_train, y_train,
    train_sizes=np.linspace(0.1, 1.0, 10),
    cv=5, scoring="r2"
)
```

**Output format** (JSON):
```json
{
    "train_sizes": [500, 1000, ...],
    "models": {
        "xgboost": {
            "train_r2_mean": [...],
            "train_r2_std": [...],
            "test_r2_mean": [...],
            "test_r2_std": [...]
        }
    }
}
```

---

## Code Style

Same conventions as `physics-engine`:
- Type hints on all functions
- `logging` module, no `print()`
- Vectorized pandas/numpy operations, no `iterrows()`
- Docstrings with parameter descriptions

```python
import logging
from sklearn.ensemble import RandomForestRegressor
import numpy as np

logger = logging.getLogger(__name__)

def train_model(
    model_slug: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
) -> tuple[object, dict]:
    """
    Train a single model and return it with evaluation metrics.

    Args:
        model_slug: Model identifier (e.g., "random_forest").
        X_train: Training features, shape (n_samples, n_features).
        y_train: Training targets, shape (n_samples, n_targets).

    Returns:
        Tuple of (fitted model, metrics dict).
    """
    logger.info(f"Training {model_slug}...")
    # ...
```

---

## Testing Strategy

**Framework:** pytest  
**Coverage target:** ≥85%

| Category | What it tests |
|----------|--------------|
| **Registry** | Load all 8 models, predict_all returns correct structure |
| **Prediction shape** | predict() returns (n_samples, 2) for all models |
| **Metrics computation** | R², MAE, RMSE computed correctly against known values |
| **Serialization roundtrip** | Save → load → predict produces identical results |
| **Feature importance** | Tree-based models return importances summing to 1.0 |
| **Cross-validation** | cv_scores has correct shape (5 folds) |
| **Scaler persistence** | Scaler saved and loaded correctly, transform matches |
| **Edge cases** | Single-sample prediction, all-zero features |

---

## Boundaries

### Always Do
- Scale features before training (StandardScaler)
- Save the scaler alongside models
- Log training time for each model
- Use `random_state=42` for reproducibility everywhere
- Compute metrics on the **test set** (never on training data)

### Ask First
- Adding hyperparameter search (GridSearchCV, Optuna)
- Adding new model types
- Changing the train/test split ratio

### Never Do
- Evaluate on training data and report those metrics
- Use `iterrows()` or Python loops over DataFrames
- Hardcode file paths
- Train without a fixed random seed

---

## Success Criteria

1. All 8 models train successfully without errors
2. XGBoost achieves R² > 0.95 on both targets (frequency and gain)
3. Linear Regression R² is meaningfully lower than XGBoost (demonstrating non-linear value)
4. All models produce predictions within physically plausible ranges
5. Feature importance shows `Patch_L` as top feature for frequency (physics expects this)
6. Learning curves show diminishing returns after ~5,000 samples (validates dataset size)
7. All serialized models load correctly and reproduce predictions
8. Training pipeline completes in <5 minutes for all 8 models
9. All analysis outputs (metrics.json, feature_importance.json, learning_curves.json, cross_validation.json) are valid JSON consumed by the frontend
