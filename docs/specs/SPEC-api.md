# Spec: api

> **Module ID:** `api`  
> **Capability Map:** [capability_map.md](file:///Users/himaghnaroy/.gemini/antigravity-ide/brain/b5b0a198-c758-41d8-a785-cb83ea463b44/capability_map.md)  
> **Depends on:** `physics-engine`, `ml-models`  
> **Consumed by:** `frontend`

---

## Objective

Expose the physics engine and ML models through a RESTful API that the React frontend consumes. The API must support:
1. **Real-time prediction** — physics engine + all 8 ML models in a single call
2. **Radiation pattern** — full θ/φ grid for 2D polar and 3D surface plots
3. **S₁₁ frequency sweep** — return loss data for plotting
4. **DGS equivalent circuit** — L, C, frequency shift for each slot
5. **Model comparison** — pre-computed metrics, feature importance, learning curves
6. **CORS** — allow frontend dev server to call the API

---

## Tech Stack

- **Framework:** FastAPI (Python 3.10+)
- **ASGI server:** Uvicorn
- **Dependencies:** fastapi, uvicorn, pydantic, numpy, `physics-engine`, `ml-models`
- **CORS:** `fastapi.middleware.cors.CORSMiddleware`

---

## Commands

```bash
# Start the API server (development)
uvicorn backend.api.main:app --reload --port 8000

# Start the API server (production)
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000

# Run API tests
pytest backend/api/tests/ -v

# Health check
curl http://localhost:8000/api/health
```

---

## Project Structure

```
backend/api/
├── __init__.py
├── main.py              # FastAPI app, CORS config, lifespan (load models)
├── routes/
│   ├── __init__.py
│   ├── predict.py       # POST /api/predict
│   ├── pattern.py       # POST /api/pattern
│   ├── s_parameter.py   # POST /api/s-parameter
│   ├── dgs.py           # POST /api/dgs/circuit
│   ├── models.py        # GET /api/models/*
│   └── health.py        # GET /api/health
├── schemas.py           # Pydantic request/response models
├── dependencies.py      # Shared dependencies (physics engine, model registry)
└── tests/
    ├── test_predict.py
    ├── test_pattern.py
    ├── test_models.py
    └── conftest.py      # Test fixtures (test client, mock data)
```

---

## API Endpoints

### `POST /api/predict`

Main prediction endpoint. Returns physics engine result + all 8 ML model predictions.

**Request:**
```json
{
    "substrate": {
        "width_mm": 40.0,
        "length_mm": 40.0,
        "height_mm": 1.6,
        "epsilon_r": 4.4,
        "tan_delta": 0.02
    },
    "patch": {
        "width_mm": 30.0,
        "length_mm": 23.0
    },
    "feed": {
        "width_mm": 3.0,
        "inset_mm": 7.0
    },
    "slots": [
        {
            "width_mm": 2.0,
            "length_mm": 8.0,
            "x_mm": 20.0,
            "y_mm": 20.0
        }
    ]
}
```

**Response:**
```json
{
    "physics": {
        "freq_ghz": 2.41,
        "gain_dbi": 6.2,
        "bandwidth_ghz": 0.08,
        "s11_min_db": -22.5
    },
    "models": {
        "linear_regression": {"freq_ghz": 2.38, "gain_dbi": 5.9},
        "ridge": {"freq_ghz": 2.39, "gain_dbi": 5.95},
        "lasso": {"freq_ghz": 2.37, "gain_dbi": 5.8},
        "knn": {"freq_ghz": 2.42, "gain_dbi": 6.3},
        "decision_tree": {"freq_ghz": 2.40, "gain_dbi": 6.1},
        "random_forest": {"freq_ghz": 2.41, "gain_dbi": 6.15},
        "xgboost": {"freq_ghz": 2.41, "gain_dbi": 6.18},
        "svr": {"freq_ghz": 2.40, "gain_dbi": 6.0}
    },
    "dgs_circuits": [
        {
            "slot_index": 0,
            "L_nH": 1.23,
            "C_pF": 0.45,
            "f_dgs_ghz": 6.8,
            "delta_f_ratio": -0.032,
            "delta_gain_dbi": -0.15
        }
    ],
    "cavity_model": {
        "epsilon_eff": 4.01,
        "delta_L_mm": 0.74,
        "L_eff_mm": 24.48,
        "f_unperturbed_ghz": 2.49
    }
}
```

---

### `POST /api/pattern`

Compute the full radiation pattern.

**Request:**
```json
{
    "substrate": { ... },
    "patch": { ... },
    "feed": { ... },
    "slots": [ ... ],
    "theta_resolution": 181,
    "phi_resolution": 361
}
```

**Response:**
```json
{
    "theta_deg": [0, 1, 2, ..., 180],
    "phi_deg": [0, 1, 2, ..., 360],
    "gain_pattern_db": [[...]],
    "e_plane_db": [...],
    "h_plane_db": [...],
    "peak_gain_dbi": 6.2,
    "beamwidth_e_deg": 78.5,
    "beamwidth_h_deg": 92.3
}
```

**Note:** This is a larger payload (~250KB for 181×361 grid). Consider reducing resolution for real-time updates and full resolution on-demand.

---

### `POST /api/s-parameter`

Compute S₁₁ return loss vs frequency.

**Request:**
```json
{
    "substrate": { ... },
    "patch": { ... },
    "feed": { ... },
    "slots": [ ... ],
    "freq_start_ghz": 1.0,
    "freq_stop_ghz": 5.0,
    "num_points": 500
}
```

**Response:**
```json
{
    "freq_ghz": [1.0, 1.008, ...],
    "s11_db": [-1.2, -1.3, ...],
    "z_in_real": [150.0, 148.5, ...],
    "z_in_imag": [45.0, 42.3, ...],
    "resonant_freq_ghz": 2.41,
    "bandwidth_ghz": 0.08,
    "min_s11_db": -22.5
}
```

---

### `POST /api/dgs/circuit`

Compute equivalent circuit for a single DGS slot.

**Request:**
```json
{
    "slot": { "width_mm": 2.0, "length_mm": 8.0, "x_mm": 20.0, "y_mm": 20.0 },
    "substrate": { ... },
    "patch": { ... }
}
```

**Response:**
```json
{
    "L_nH": 1.23,
    "C_pF": 0.45,
    "f_dgs_ghz": 6.8,
    "delta_f_ratio": -0.032,
    "f_perturbed_ghz": 2.41,
    "delta_gain_dbi": -0.15
}
```

---

### `GET /api/models/compare`

Return pre-computed evaluation metrics for all models.

**Response:**
```json
{
    "models": {
        "xgboost": {
            "category": "Ensemble (Boosting)",
            "freq": {"r2": 0.997, "mae": 0.02, "rmse": 0.03},
            "gain": {"r2": 0.953, "mae": 0.18, "rmse": 0.25},
            "overall_r2": 0.975,
            "training_time_s": 2.3
        },
        "linear_regression": { ... },
        ...
    },
    "ranking": ["xgboost", "random_forest", "knn", ...],
    "best_model": "xgboost"
}
```

---

### `GET /api/models/feature-importance`

**Response:** Pre-computed feature importance JSON (see ml-models spec).

### `GET /api/models/learning-curves`

**Response:** Pre-computed learning curve JSON (see ml-models spec).

### `GET /api/models/cross-validation`

**Response:** Pre-computed cross-validation JSON.

### `GET /api/health`

**Response:**
```json
{
    "status": "ok",
    "models_loaded": 8,
    "physics_engine": "ready"
}
```

---

## Pydantic Schemas (`schemas.py`)

```python
from pydantic import BaseModel, Field, field_validator

class SubstrateInput(BaseModel):
    width_mm: float = Field(..., gt=0, le=100, description="Substrate width in mm")
    length_mm: float = Field(..., gt=0, le=100)
    height_mm: float = Field(..., gt=0.1, le=5.0)
    epsilon_r: float = Field(..., gt=1.0, le=15.0)
    tan_delta: float = Field(..., gt=0, le=0.1)

class PatchInput(BaseModel):
    width_mm: float = Field(..., gt=1.0, le=80)
    length_mm: float = Field(..., gt=1.0, le=80)

class FeedInput(BaseModel):
    width_mm: float = Field(..., gt=0.1, le=10)
    inset_mm: float = Field(0.0, ge=0)

class SlotInput(BaseModel):
    width_mm: float = Field(..., gt=0, le=20)
    length_mm: float = Field(..., gt=0, le=30)
    x_mm: float = Field(..., description="Slot center X on ground plane")
    y_mm: float = Field(..., description="Slot center Y on ground plane")

class PredictRequest(BaseModel):
    substrate: SubstrateInput
    patch: PatchInput
    feed: FeedInput
    slots: list[SlotInput] = Field(default_factory=list, max_length=2)

    @field_validator("slots")
    @classmethod
    def validate_slot_count(cls, v):
        if len(v) > 2:
            raise ValueError("Maximum 2 DGS slots supported")
        return v
```

---

## App Configuration (`main.py`)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load ML models into memory
    app.state.model_registry = ModelRegistry("backend/ml_models/saved_models/")
    logger.info(f"Loaded {len(app.state.model_registry.models)} ML models")
    yield
    # Shutdown: cleanup

app = FastAPI(
    title="Antenna DGS Predictor API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Code Style

Same conventions as other modules. FastAPI-specific additions:
- Use Pydantic models for all request/response validation
- Use dependency injection for shared state (model registry, physics engine)
- Return appropriate HTTP status codes (422 for validation errors, 500 for engine errors)
- Use `logging` for request tracking

---

## Testing Strategy

**Framework:** pytest + httpx (FastAPI TestClient)  
**Coverage target:** ≥85%

| Category | What it tests |
|----------|--------------|
| **Predict endpoint** | Valid request returns physics + all 8 ML predictions |
| **Pattern endpoint** | Returns correct array shapes |
| **S-parameter endpoint** | Returns freq sweep with S₁₁ dip at resonance |
| **Validation** | Invalid inputs (negative dimensions, patch > substrate) return 422 |
| **Model comparison** | /models/compare returns metrics for all 8 models |
| **Health check** | /health returns status ok |
| **CORS** | Preflight request from localhost:5173 succeeds |
| **Error handling** | Physics engine errors return meaningful error messages |

---

## Boundaries

### Always Do
- Validate all inputs with Pydantic (constraints on ranges)
- Return physics engine + all ML model results in the predict endpoint
- Load models once at startup (not per-request)
- Include CORS middleware for the frontend dev server

### Ask First
- Adding authentication
- Adding rate limiting
- Changing response schema structure

### Never Do
- Expose internal file paths in error messages
- Return raw Python exceptions to the client
- Train models via the API (training is an offline CLI operation)

---

## Success Criteria

1. All endpoints return correct response schemas
2. `/api/predict` responds in <200ms for a single configuration
3. `/api/pattern` responds in <500ms with full resolution
4. Pydantic validation catches invalid inputs and returns helpful error messages
5. All 8 ML models are loaded at startup and available for prediction
6. CORS allows the frontend dev server (localhost:5173) to make requests
7. Health endpoint confirms all models loaded
