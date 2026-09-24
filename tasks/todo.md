# Tasks: Antenna DGS Predictor

> Plan: [tasks/plan.md](file:///Users/himaghnaroy/Desktop/minor_project/tasks/plan.md)  
> Constraints: [CONSTRAINTS.md](file:///Users/himaghnaroy/Desktop/minor_project/CONSTRAINTS.md)

---

## Phase 1: Physics Engine

### Task 1: Project scaffolding + constants + types

**Description:** Create the `backend/` package structure, physical constants module, and all dataclasses (`AntennaConfig`, `SubstrateConfig`, `PatchConfig`, `FeedConfig`, `DGSSlot`). Set up `pyproject.toml` with dependencies (numpy, scipy, fastapi, uvicorn, scikit-learn, xgboost, pandas, joblib, pytest, pytest-cov). Add `__init__.py` files. Create the `backend/physics_engine/` subpackage skeleton.

**Acceptance criteria:**
- [x] `backend/` and `backend/physics_engine/` are importable Python packages
- [x] `backend.physics_engine.types` exports all 5 dataclasses + `SUBSTRATES` dict
- [x] `backend.physics_engine.constants` exports `c`, `epsilon_0`, `mu_0`, `sigma_copper`
- [x] `pyproject.toml` installs cleanly with `pip install -e .`

**Verification:**
- [x] `python -c "from backend.physics_engine.types import AntennaConfig"` succeeds
- [x] `pytest backend/physics_engine/tests/test_types.py -v` passes
- [x] Build succeeds: `pip install -e .`

**Dependencies:** None

**Files likely touched:**
- `backend/__init__.py`
- `backend/physics_engine/__init__.py`
- `backend/physics_engine/constants.py`
- `backend/physics_engine/types.py`
- `backend/physics_engine/tests/__init__.py`
- `backend/physics_engine/tests/test_types.py`
- `pyproject.toml`

**Estimated scope:** S (1-2 files of logic, rest is boilerplate)

---

### Task 2: Cavity model — resonant frequency

**Description:** Implement `cavity_model.py` with `effective_permittivity()`, `fringing_extension()`, and `resonant_frequency()`. All equations from Hammerstad. Internal units: SI (meters, Hz). Conversion to mm/GHz only at public API boundary.

**Acceptance criteria:**
- [x] `effective_permittivity(ε_r, h, w)` returns correct ε_eff
- [x] `fringing_extension(ε_eff, h, w)` returns ΔL in meters
- [x] `resonant_frequency(config)` returns f_r in Hz (no DGS, bare patch)
- [x] FR4 (ε_r=4.4), h=1.6mm, W=38mm, L=29mm → f_r ≈ 2.4 GHz (±5%)
- [x] Rogers 5880 (ε_r=2.2), h=0.787mm, W=15mm, L=12mm → f_r ≈ 8.5 GHz (±5%)

**Verification:**
- [x] `pytest backend/physics_engine/tests/test_cavity_model.py -v` passes
- [x] Known-answer tests for 3+ antenna configs within ±5%
- [x] Monotonicity test: increasing L → decreasing f_r

**Dependencies:** Task 1

**Files likely touched:**
- `backend/physics_engine/cavity_model.py`
- `backend/physics_engine/tests/test_cavity_model.py`

**Estimated scope:** S

---

### Task 3: Gain model — directivity & radiation efficiency

**Description:** Implement `gain_model.py` with `radiation_conductance()`, `directivity()`, `radiation_efficiency()`, and `gain()`. Uses Balanis approximations for conductance. Accounts for dielectric, conductor, and surface wave losses.

**Acceptance criteria:**
- [x] `gain(config)` returns G in dBi
- [x] Standard rectangular patches produce gain in 2–8 dBi range
- [x] Radiation efficiency is between 0 and 1
- [x] FR4 patch produces lower efficiency than Rogers (higher tanδ = more loss)

**Verification:**
- [x] `pytest backend/physics_engine/tests/test_gain_model.py -v` passes
- [x] Physical bounds test: gain ∈ [0, 12] dBi for all tested configs
- [x] Efficiency ordering: η(FR4) < η(Rogers 5880)

**Dependencies:** Task 2 (needs ε_eff, f_r)

**Files likely touched:**
- `backend/physics_engine/gain_model.py`
- `backend/physics_engine/tests/test_gain_model.py`

**Estimated scope:** S

---

### Task 4: Radiation pattern — far-field E(θ, φ)

**Description:** Implement `radiation.py` with `e_plane_pattern()`, `h_plane_pattern()`, and `full_pattern()`. Dual-slot model. Returns normalized gain in dB on a θ×φ grid.

**Acceptance criteria:**
- [x] `full_pattern(config)` returns dict with `theta_deg`, `phi_deg`, `gain_pattern_db`, `e_plane_db`, `h_plane_db`
- [x] Main lobe is broadside (θ = 0°)
- [x] Pattern is symmetric: E_plane(θ) = E_plane(-θ)
- [x] 3dB beamwidth in 60°–120° range for typical patches
- [x] Back lobe suppression ≥ 10 dB

**Verification:**
- [x] `pytest backend/physics_engine/tests/test_radiation.py -v` passes
- [x] Symmetry test passes
- [x] Peak at θ=0° confirmed
- [x] No NaN/Inf in output arrays

**Dependencies:** Task 2 (needs f_r for k₀)

**Files likely touched:**
- `backend/physics_engine/radiation.py`
- `backend/physics_engine/tests/test_radiation.py`

**Estimated scope:** M (sinc functions, 2D grid computation, multiple output arrays)

---

### Task 5: Impedance & S₁₁ — return loss vs frequency

**Description:** Implement `impedance.py` with `edge_resistance()`, `input_impedance()`, `quality_factor()`, and `s_parameter()`. Transmission line model with Q-factor approach. Returns S₁₁ across a frequency sweep.

**Acceptance criteria:**
- [x] `s_parameter(config)` returns dict with `freq_ghz`, `s11_db`, `z_in_real`, `z_in_imag`, `bandwidth_ghz`
- [x] S₁₁ minimum occurs within ±2% of the computed resonant frequency
- [x] S₁₁ dip is < -10 dB for a well-matched antenna (inset feed at 50Ω)
- [x] Bandwidth is positive and physically plausible (1–10% of f_r)

**Verification:**
- [x] `pytest backend/physics_engine/tests/test_impedance.py -v` passes
- [x] S₁₁ resonance test: argmin(S₁₁) within ±2% of f_r
- [x] No NaN/Inf in sweep arrays

**Dependencies:** Task 2, Task 3 (needs f_r, G₁ for edge resistance)

**Files likely touched:**
- `backend/physics_engine/impedance.py`
- `backend/physics_engine/tests/test_impedance.py`

**Estimated scope:** M

---

### Task 6: DGS model — equivalent circuit & perturbation

**Description:** Implement `dgs_model.py` with `slot_capacitance()`, `slot_inductance()`, `slot_resonant_frequency()`, `coupling_coefficient()`, `frequency_perturbation()`, and `gain_perturbation()`. Wire DGS into the public API so `resonant_frequency(config_with_slots)` and `gain(config_with_slots)` automatically include perturbation.

**Acceptance criteria:**
- [x] `dgs_equivalent_circuit(slot, config)` returns L_nH, C_pF, f_dgs_ghz, delta_f_ratio
- [x] No-slot config → zero perturbation (Δf = 0, ΔG = 0)
- [x] Adding a slot lowers frequency (delta_f_ratio < 0)
- [x] Larger slot area → larger |Δf|
- [x] Two non-overlapping slots: perturbations are additive
- [x] `full_analysis(config)` returns all outputs in one dict

**Verification:**
- [x] `pytest backend/physics_engine/tests/test_dgs_model.py -v` passes
- [x] `pytest backend/physics_engine/tests/test_integration.py -v` passes (end-to-end)
- [x] `python -m backend.physics_engine.validate` prints sensible results

**Dependencies:** Task 2, Task 3, Task 4, Task 5

**Files likely touched:**
- `backend/physics_engine/dgs_model.py`
- `backend/physics_engine/__init__.py` (public API: `full_analysis()`)
- `backend/physics_engine/validate.py`
- `backend/physics_engine/tests/test_dgs_model.py`
- `backend/physics_engine/tests/test_integration.py`

**Estimated scope:** M

---

## Checkpoint: Phase 1 Complete
- [x] All physics engine tests pass: `pytest backend/physics_engine/tests/ -v`
- [x] `python -m backend.physics_engine.validate` prints correct results for 3+ known configs
- [x] Known-answer tests within ±5% for frequency, ±1 dBi for gain
- [x] No NaN/Inf in any output
- [x] `floor-guard` clean: `node floor-guard.mjs`

---

## Phase 2: Data Generator

### Task 7: LHS sampler + physical constraints

**Description:** Implement `sampler.py` (Latin Hypercube Sampling with physical constraints) and `constraints.py` (validation checks). The sampler draws from the full parameter space, applies constraints, and rejects invalid samples.

**Acceptance criteria:**
- [x] `sample_parameters(n, seed)` returns n parameter sets via LHS
- [x] `validate_sample(sample)` checks all physical constraints (patch < substrate, slot inside ground, etc.)
- [x] Substrate materials sampled from weighted preset list (40% FR4, 20% Rogers 5880, etc.)
- [x] Rejection rate < 5% with well-tuned ranges
- [x] Same seed → identical samples

**Verification:**
- [x] `pytest backend/data_generator/tests/test_sampler.py -v` passes
- [x] `pytest backend/data_generator/tests/test_constraints.py -v` passes
- [x] Determinism test: two runs with same seed produce identical output

**Dependencies:** Task 1 (types)

**Files likely touched:**
- `backend/data_generator/__init__.py`
- `backend/data_generator/sampler.py`
- `backend/data_generator/constraints.py`
- `backend/data_generator/tests/test_sampler.py`
- `backend/data_generator/tests/test_constraints.py`

**Estimated scope:** M

---

### Task 8: Dataset generation pipeline

**Description:** Implement `generate.py` — the CLI script that ties the sampler to the physics engine. Generates 10,000 samples, runs each through `full_analysis()`, validates outputs, and exports to CSV + Parquet.

**Acceptance criteria:**
- [x] CLI: `python -m backend.data_generator.generate --samples 10000 --seed 42 --output backend/data/antenna_dataset.csv`
- [x] Output CSV has all 23 columns (18 features + 5 outputs)
- [x] Zero NaN/Inf in the dataset
- [x] 100% of samples pass `validate_sample()`
- [x] Parquet file also generated alongside CSV
- [x] Completes in < 5 minutes for 10,000 samples

**Verification:**
- [x] `pytest backend/data_generator/tests/test_generate.py -v` passes (small dataset, 100 samples)
- [x] `python -m backend.data_generator.generate --samples 100 --seed 42 --output backend/data/test_dataset.csv` runs successfully
- [x] `python -m backend.data_generator.validate --input backend/data/test_dataset.csv` confirms all constraints pass

**Dependencies:** Task 6 (full physics engine), Task 7 (sampler)

**Files likely touched:**
- `backend/data_generator/generate.py`
- `backend/data_generator/validate.py`
- `backend/data_generator/tests/test_generate.py`

**Estimated scope:** M

---

## Checkpoint: Phase 2 Complete
- [x] `python -m backend.data_generator.generate --samples 100 --seed 42` produces valid dataset
- [x] All data generator tests pass
- [x] Generated dataset has 100% valid samples
- [x] `floor-guard` clean

---

## Phase 3: ML Models

### Task 9: Training pipeline + model registry

**Description:** Implement `preprocessing.py` (feature scaling, train/test split), `train.py` (CLI training pipeline for all 8 models), and `registry.py` (unified interface for loading and predicting with any model).

**Acceptance criteria:**
- [x] `train.py` CLI trains all 8 models and saves them as `.joblib` files
- [x] `StandardScaler` is fitted on training data and saved alongside models
- [x] `ModelRegistry` loads all models and provides `predict()`, `predict_all()`, `compare()`
- [x] `metadata.json` records training date, dataset hash, hyperparameters
- [x] All models produce predictions in physically plausible ranges

**Verification:**
- [x] `pytest backend/ml_models/tests/test_train.py -v` passes (trains on small dataset)
- [x] `pytest backend/ml_models/tests/test_registry.py -v` passes
- [x] Serialization roundtrip: save → load → predict produces identical results

**Dependencies:** Task 8 (dataset)

**Files likely touched:**
- `backend/ml_models/__init__.py`
- `backend/ml_models/preprocessing.py`
- `backend/ml_models/train.py`
- `backend/ml_models/registry.py`
- `backend/ml_models/tests/test_train.py`
- `backend/ml_models/tests/test_registry.py`

**Estimated scope:** M

---

### Task 10: Evaluation — metrics & cross-validation

**Description:** Implement `evaluate.py` — computes R², MAE, RMSE, MAPE, max error for each model on each target. Runs 5-fold cross-validation. Saves all results to `analysis/metrics.json` and `analysis/cross_validation.json`.

**Acceptance criteria:**
- [x] Per-model, per-target metrics computed: R², MAE, RMSE, MAPE, max_error
- [x] 5-fold cross-validation scores computed and saved
- [x] XGBoost R² > 0.95 on both targets
- [x] Linear Regression R² meaningfully lower than XGBoost
- [x] Results saved as valid JSON consumable by the frontend

**Verification:**
- [x] `pytest backend/ml_models/tests/test_evaluate.py -v` passes
- [x] `metrics.json` and `cross_validation.json` are valid JSON
- [x] Ranking: XGBoost or Random Forest is #1 or #2

**Dependencies:** Task 9

**Files likely touched:**
- `backend/ml_models/evaluate.py`
- `backend/ml_models/analysis/metrics.json` (generated)
- `backend/ml_models/analysis/cross_validation.json` (generated)
- `backend/ml_models/tests/test_evaluate.py`

**Estimated scope:** S

---

### Task 11: Analysis — feature importance & learning curves

**Description:** Implement `analysis.py` — computes feature importance (tree-based + linear coefficients), learning curves (R² vs training set size). Saves to JSON for frontend consumption.

**Acceptance criteria:**
- [x] Feature importance for tree-based models (importances sum to ~1.0)
- [x] Linear model coefficients as importance proxy
- [x] Lasso zero-coefficient features identified
- [x] Learning curves: R² vs 10 training set fractions (10% to 100%)
- [x] `Patch_L` is top feature for frequency prediction
- [x] All results saved as valid JSON

**Verification:**
- [x] `pytest backend/ml_models/tests/test_analysis.py -v` passes
- [x] `feature_importance.json` and `learning_curves.json` are valid JSON
- [x] Feature importance values are non-negative and sum to ~1.0 for tree models

**Dependencies:** Task 9

**Files likely touched:**
- `backend/ml_models/analysis.py`
- `backend/ml_models/analysis/feature_importance.json` (generated)
- `backend/ml_models/analysis/learning_curves.json` (generated)
- `backend/ml_models/tests/test_analysis.py`

**Estimated scope:** S

---

## Checkpoint: Phase 3 Complete
- [x] All 8 models trained and serialized: `ls backend/ml_models/saved_models/*.joblib`
- [x] All ML model tests pass
- [x] All analysis JSONs are valid and populated
- [x] XGBoost R² > 0.95
- [x] `floor-guard` clean

---

## Phase 4: API Layer

### Task 12: FastAPI app + predict endpoint

**Description:** Create the FastAPI application with CORS middleware, lifespan handler (loads models at startup), Pydantic schemas for request/response validation, and the main `POST /api/predict` endpoint that returns physics engine + all ML model predictions.

**Acceptance criteria:**
- [x] `POST /api/predict` accepts antenna config JSON and returns physics + 8 ML predictions
- [x] Pydantic validates inputs (positive dimensions, patch < substrate, max 2 slots)
- [x] Invalid inputs return 422 with helpful error messages
- [x] All 8 ML models loaded at startup (not per-request)
- [x] Response includes `cavity_model` intermediate values (ε_eff, ΔL, L_eff)
- [x] CORS allows `localhost:5173`

**Verification:**
- [x] `pytest backend/api/tests/test_predict.py -v` passes
- [x] Manual test with `curl` returns correct JSON structure
- [x] Invalid input returns 422, not 500

**Dependencies:** Task 6 (physics engine), Task 9 (model registry)

**Files likely touched:**
- `backend/api/__init__.py`
- `backend/api/main.py`
- `backend/api/schemas.py`
- `backend/api/dependencies.py`
- `backend/api/routes/__init__.py`
- `backend/api/routes/predict.py`
- `backend/api/routes/health.py`
- `backend/api/tests/conftest.py`
- `backend/api/tests/test_predict.py`

**Estimated scope:** M

---

### Task 13: Pattern + S-parameter endpoints

**Description:** Add `POST /api/pattern` (radiation pattern) and `POST /api/s-parameter` (return loss sweep) endpoints.

**Acceptance criteria:**
- [x] `POST /api/pattern` returns full θ×φ gain grid + E/H-plane cuts + beamwidth
- [x] `POST /api/s-parameter` returns freq sweep with S₁₁, Z_in, bandwidth
- [x] Both endpoints accept resolution/range parameters
- [x] Response sizes are reasonable (<500KB for pattern)

**Verification:**
- [x] `pytest backend/api/tests/test_pattern.py -v` passes
- [x] Pattern response has correct array shapes
- [x] S-parameter response has S₁₁ dip at resonant frequency

**Dependencies:** Task 12

**Files likely touched:**
- `backend/api/routes/pattern.py`
- `backend/api/routes/s_parameter.py`
- `backend/api/tests/test_pattern.py`

**Estimated scope:** S

---

### Task 14: Model comparison + DGS circuit endpoints

**Description:** Add `GET /api/models/compare`, `GET /api/models/feature-importance`, `GET /api/models/learning-curves`, `GET /api/models/cross-validation`, and `POST /api/dgs/circuit` endpoints.

**Acceptance criteria:**
- [x] `/api/models/compare` returns metrics for all 8 models with ranking
- [x] `/api/models/feature-importance` returns feature importance data
- [x] `/api/models/learning-curves` returns learning curve data
- [x] `/api/dgs/circuit` returns L, C, f_dgs, delta_f for a given slot
- [x] All endpoints return valid JSON consumed by the frontend

**Verification:**
- [x] `pytest backend/api/tests/test_models.py -v` passes
- [x] All GET endpoints return 200 with correct JSON structure
- [x] `/api/health` confirms all models loaded

**Dependencies:** Task 12, Task 10, Task 11

**Files likely touched:**
- `backend/api/routes/models.py`
- `backend/api/routes/dgs.py`
- `backend/api/tests/test_models.py`

**Estimated scope:** S

---

## Checkpoint: Phase 4 Complete
- [x] API server starts: `uvicorn backend.api.main:app --reload`
- [x] All API tests pass
- [x] `GET /api/health` returns `{"status": "ok", "models_loaded": 8}`
- [x] `POST /api/predict` with a sample config returns physics + 8 ML predictions
- [x] `floor-guard` clean

---

## Phase 5: Frontend

### Task 15: Vite + React scaffold + design system

**Description:** Initialize the Vite + React project in `frontend/`. Set up `index.css` with the full design system (color tokens, glassmorphism, typography, spacing, transitions). Create shared components: `GlassCard`, `AnimatedNumber`, `LoadingSpinner`. Import Google Fonts (Inter, JetBrains Mono). Dark mode as default.

**Acceptance criteria:**
- [x] `npm run dev` serves the app at `localhost:5173`
- [x] All CSS custom properties defined in `:root`
- [x] `GlassCard` renders with backdrop-filter blur + border
- [x] `AnimatedNumber` smoothly transitions between values
- [x] Fonts load correctly (Inter for UI, JetBrains Mono for data)
- [x] Page is dark-mode by default, no white flash

**Verification:**
- [x] `npm run dev` starts without errors
- [x] Browser shows styled dark page with glass card
- [x] No console errors

**Dependencies:** None (frontend can be scaffolded independently)

**Files likely touched:**
- `frontend/index.html`
- `frontend/package.json`
- `frontend/vite.config.js`
- `frontend/src/main.jsx`
- `frontend/src/App.jsx`
- `frontend/src/index.css`
- `frontend/src/components/shared/GlassCard.jsx`
- `frontend/src/components/shared/AnimatedNumber.jsx`
- `frontend/src/components/shared/LoadingSpinner.jsx`
- `frontend/src/components/shared/shared.css`

**Estimated scope:** M

---

### Task 16: Layout + sidebar controls

**Description:** Build the page layout (header, sidebar, main content area) and the sidebar controls (substrate material preset, dimension sliders for substrate/patch/feed, slot add/remove/configure). Wire to `useAntennaConfig` hook.

**Acceptance criteria:**
- [x] Sidebar is fixed-width (320px) on the left
- [x] All dimension sliders work and show current value + unit
- [x] Substrate preset dropdown changes ε_r and tanδ automatically
- [x] Slot controls: add up to 2 slots, remove, configure width/length/position
- [x] `useAntennaConfig` hook manages all antenna state

**Verification:**
- [x] All sliders are interactive and update state
- [x] Adding/removing slots updates the config
- [x] No console errors

**Dependencies:** Task 15

**Files likely touched:**
- `frontend/src/components/Layout/Header.jsx`
- `frontend/src/components/Layout/Sidebar.jsx`
- `frontend/src/components/Layout/Layout.css`
- `frontend/src/components/Controls/DimensionSliders.jsx`
- `frontend/src/components/Controls/SubstratePresets.jsx`
- `frontend/src/components/Controls/SlotControls.jsx`
- `frontend/src/components/Controls/Controls.css`
- `frontend/src/hooks/useAntennaConfig.js`
- `frontend/src/utils/constants.js`

**Estimated scope:** M

---

### Task 17: API client + prediction cards (Layer 1)

**Description:** Build the API client module (`api/client.js`) and wire it to the prediction display. Create `PredictionCards` component showing Frequency, Gain, Bandwidth with `AnimatedNumber`. Create `usePrediction` hook that debounces API calls (300ms) on config change.

**Acceptance criteria:**
- [x] `api/client.js` exports `predict()`, `getPattern()`, `getSParameter()`, `getModelComparison()`, etc.
- [x] `usePrediction` debounces at 300ms before calling the API
- [x] `PredictionCards` shows animated Frequency (GHz), Gain (dBi), Bandwidth (MHz)
- [x] Loading state shown during API calls
- [x] Error state shown on API failure (doesn't crash)

**Verification:**
- [x] Moving a slider triggers a debounced API call (visible in Network tab)
- [x] Prediction cards update with smooth number animation
- [x] Disconnecting the API shows error state, not crash

**Dependencies:** Task 15, Task 16, Task 12 (API must be running)

**Files likely touched:**
- `frontend/src/api/client.js`
- `frontend/src/hooks/usePrediction.js`
- `frontend/src/components/Results/PredictionCards.jsx`
- `frontend/src/components/Results/Results.css`
- `frontend/src/utils/debounce.js`
- `frontend/src/utils/formatters.js`

**Estimated scope:** M

---

### Task 18: Antenna canvas (SVG schematic)

**Description:** Build the `AntennaCanvas` component — an SVG rendering of the antenna (top-down view). Shows ground plane, substrate, patch, feed line, DGS slots with dimension annotations. Scales proportionally. Updates instantly on config change (no API call needed — pure local rendering).

**Acceptance criteria:**
- [x] Ground plane, patch, feed line rendered as rectangles
- [x] DGS slots rendered with dashed border in contrasting color
- [x] Dimension labels with arrows showing W, L, H values
- [x] Canvas auto-scales to fit the antenna proportionally
- [x] Instant update on slider change (no debounce needed)

**Verification:**
- [x] Changing patch width visually changes the patch rectangle
- [x] Adding a slot shows the slot on the ground plane
- [x] Dimension labels update in real-time

**Dependencies:** Task 16 (needs config state)

**Files likely touched:**
- `frontend/src/components/AntennaCanvas/AntennaCanvas.jsx`
- `frontend/src/components/AntennaCanvas/PatchRenderer.jsx`
- `frontend/src/components/AntennaCanvas/SlotRenderer.jsx`
- `frontend/src/components/AntennaCanvas/DimensionLabels.jsx`
- `frontend/src/components/AntennaCanvas/AntennaCanvas.css`

**Estimated scope:** M

---

### Task 19: Radiation pattern + S₁₁ plots (Plotly)

**Description:** Implement `PolarPattern` (2D polar plot of E/H-plane), `Pattern3D` (3D radiation surface), and `SParameterPlot` (S₁₁ vs frequency line chart). All using Plotly.js. Wire to `usePattern` hook that fetches data on-demand or debounced (500ms).

**Acceptance criteria:**
- [x] 2D polar pattern renders with E-plane and H-plane traces
- [x] 3D radiation surface renders and is rotatable/zoomable
- [x] S₁₁ plot shows clear resonance dip with -10dB line marked
- [x] All charts use dark theme matching the design system
- [x] Charts resize with their container

**Verification:**
- [x] Polar pattern shows recognizable broadside pattern
- [x] 3D surface is interactive (rotate, zoom)
- [x] S₁₁ dip is visible at the predicted frequency
- [x] No console errors from Plotly

**Dependencies:** Task 17 (API client), Task 13 (pattern/s-param endpoints)

**Files likely touched:**
- `frontend/src/components/Patterns/PolarPattern.jsx`
- `frontend/src/components/Patterns/Pattern3D.jsx`
- `frontend/src/components/Patterns/SParameterPlot.jsx`
- `frontend/src/components/Patterns/Patterns.css`
- `frontend/src/hooks/usePattern.js`

**Estimated scope:** M

---

### Task 20: Physics reveal panel (Layer 2)

**Description:** Build the `PhysicsReveal` expandable panel. Clicking a prediction card expands a section showing the cavity model equation with actual computed values substituted in, the DGS equivalent circuit diagram (SVG: L + C symbols with values), and the step-by-step derivation.

**Acceptance criteria:**
- [x] Clicking a prediction card expands the physics reveal panel (animated)
- [x] Shows cavity model: ε_eff = X, ΔL = Y mm, L_eff = Z mm, f_r = W GHz
- [x] Shows DGS circuit: L = X nH, C = Y pF, f_dgs = Z GHz, Δf = W MHz
- [x] Circuit diagram rendered as SVG (inductor coil + capacitor plates with labels)
- [x] Collapse animation on second click

**Verification:**
- [x] Panel expands/collapses smoothly
- [x] Values match the prediction cards
- [x] Circuit diagram SVG renders correctly

**Dependencies:** Task 17

**Files likely touched:**
- `frontend/src/components/Results/PhysicsReveal.jsx`
- `frontend/src/components/Results/CavityModelDetail.jsx`
- `frontend/src/components/Results/DGSCircuitDetail.jsx`

**Estimated scope:** M

---

### Task 21: Model comparison dashboard (Layer 3)

**Description:** Build the `ModelArena` collapsible section with `Leaderboard` (table), `MetricsTable`, `FeatureImportance` (bar chart), and `LearningCurves` (line chart). Fetches pre-computed data from the model comparison endpoints.

**Acceptance criteria:**
- [x] Collapsible "Model Comparison" section at the bottom of the page
- [x] Leaderboard table: all 8 models ranked by overall R², with rank badges
- [x] Metrics table: R², MAE, RMSE for freq and gain per model
- [x] Feature importance: horizontal bar chart (Plotly)
- [x] Learning curves: line chart with train/test R² (Plotly)
- [x] Live predictions: table showing each model's prediction for current config

**Verification:**
- [x] All 8 models appear in the leaderboard
- [x] Feature importance bars render correctly
- [x] Learning curves show expected diminishing returns
- [x] No console errors

**Dependencies:** Task 17, Task 14 (model comparison endpoints)

**Files likely touched:**
- `frontend/src/components/ModelComparison/ModelArena.jsx`
- `frontend/src/components/ModelComparison/Leaderboard.jsx`
- `frontend/src/components/ModelComparison/MetricsTable.jsx`
- `frontend/src/components/ModelComparison/FeatureImportance.jsx`
- `frontend/src/components/ModelComparison/LearningCurves.jsx`
- `frontend/src/components/ModelComparison/ModelComparison.css`
- `frontend/src/hooks/useModelComparison.js`

**Estimated scope:** L (5+ files, multiple charts)

---

## Checkpoint: Phase 5 Complete
- [x] Frontend loads at `localhost:5173` and calls API at `localhost:8000`
- [x] All three layers work: Design Canvas, Physics Reveal, ML Arena
- [x] Sliders → canvas update + debounced prediction → cards animate → plots render
- [x] Model comparison shows all 8 models ranked
- [x] Zero console errors during normal operation
- [x] First impression test: dark, polished, "wow"

---

## Phase 6: Cleanup & Polish

### Task 22: Remove legacy Streamlit code

**Description:** Delete old files that are no longer needed: `app.py`, `simulate_data.py`, `forward_model.py`, `inverse_model.py`, `data_processor.py`. Update `.gitignore` to cover new build artifacts. Update `README.md` with new architecture, setup instructions, and screenshots.

**Acceptance criteria:**
- [x] Legacy files deleted
- [x] `.gitignore` covers: `node_modules/`, `__pycache__/`, `*.pyc`, `.env`, `dist/`, `backend/ml_models/saved_models/*.joblib`, `backend/data/*.csv`, `backend/data/*.parquet`
- [x] `README.md` updated with: project description, setup instructions, architecture diagram, screenshots

**Verification:**
- [x] No imports of deleted files remain in the codebase
- [x] `grep -r "simulate_data\|forward_model\|inverse_model\|data_processor" backend/` returns nothing

**Dependencies:** All previous tasks

**Files likely touched:**
- `app.py` (DELETE)
- `simulate_data.py` (DELETE)
- `forward_model.py` (DELETE)
- `inverse_model.py` (DELETE)
- `data_processor.py` (DELETE)
- `.gitignore`
- `README.md`

**Estimated scope:** S

---

### Task 23: Final integration test + generate full dataset & train models

**Description:** Run the full pipeline end-to-end: generate the complete 10,000-sample dataset, train all 8 models, start the API, verify the frontend works with production data. Fix any integration issues.

**Acceptance criteria:**
- [x] 10,000-sample dataset generated successfully
- [x] All 8 models trained with R² > 0.90 on both targets
- [x] API starts and serves all endpoints
- [x] Frontend displays correct predictions, patterns, and model comparisons
- [x] Full pipeline from slider change to rendered result works end-to-end

**Verification:**
- [x] `python -m backend.data_generator.generate --samples 10000 --seed 42`
- [x] `python -m backend.ml_models.train --data backend/data/antenna_dataset.csv`
- [x] `uvicorn backend.api.main:app` starts without errors
- [x] `npm run dev` (in frontend/) shows working app
- [x] `floor-guard` clean
- [x] All pytest tests pass: `pytest backend/ -v`

**Dependencies:** All previous tasks

**Files likely touched:** (integration fixes as needed)

**Estimated scope:** M

---

## Checkpoint: Project Complete
- [x] All 23 tasks completed
- [x] All tests pass: `pytest backend/ -v`
- [x] Frontend loads and all three layers work
- [x] 10,000-sample dataset generated
- [x] 8 ML models trained and serialized
- [x] No legacy Streamlit code remains
- [x] `CONSTRAINTS.md` floor holds
- [x] README updated
- [x] Ready for presentation
