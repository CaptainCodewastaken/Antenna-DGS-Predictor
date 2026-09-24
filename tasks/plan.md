# Implementation Plan: Antenna DGS Predictor ("Physics Under Glass")

## Overview

Build a full-stack application that predicts the electromagnetic performance of rectangular microstrip patch antennas with DGS (Defected Ground Structure). The backend is a Python physics engine + 8 ML models served via FastAPI. The frontend is a React SPA with an interactive antenna canvas, radiation pattern visualizations, and a model comparison dashboard. Everything is physics-grounded — no arbitrary scaling.

**Specs:** [physics-engine](file:///Users/himaghnaroy/Desktop/minor_project/docs/specs/SPEC-physics-engine.md) · [data-generator](file:///Users/himaghnaroy/Desktop/minor_project/docs/specs/SPEC-data-generator.md) · [ml-models](file:///Users/himaghnaroy/Desktop/minor_project/docs/specs/SPEC-ml-models.md) · [api](file:///Users/himaghnaroy/Desktop/minor_project/docs/specs/SPEC-api.md) · [frontend](file:///Users/himaghnaroy/Desktop/minor_project/docs/specs/SPEC-frontend.md)  
**Constraints:** [CONSTRAINTS.md](file:///Users/himaghnaroy/Desktop/minor_project/CONSTRAINTS.md)  
**Tasks tracked in:** [tasks/todo.md](file:///Users/himaghnaroy/Desktop/minor_project/tasks/todo.md)

## Architecture Decisions

- **Sequential build order:** `physics-engine` → `data-generator` → `ml-models` → `api` → `frontend`. Each module's output is the next module's input; no shortcuts.
- **Python backend as a single package:** All backend code lives under `backend/` with subpackages. No microservices.
- **Offline training:** ML models are trained via CLI, serialized to disk (joblib), and loaded by the API at startup. Not trained per-request.
- **Clean break from Streamlit:** Existing `app.py`, `simulate_data.py`, etc. are replaced. Old files are cleaned up in the final phase.
- **Physics engine is the source of truth:** ML models are trained on physics-engine-generated data. The physics engine's output is always displayed alongside ML predictions for comparison.

## Dependency Graph

```
physics-engine (Phase 1)
    │
    ├─→ data-generator (Phase 2)
    │       │
    │       └─→ ml-models (Phase 3)
    │               │
    │               └─→ api (Phase 4) ←── physics-engine (also direct dep)
    │                       │
    │                       └─→ frontend (Phase 5)
    │
    └─→ api (Phase 4, direct dep for real-time predictions)
```

## Task List

See [tasks/todo.md](file:///Users/himaghnaroy/Desktop/minor_project/tasks/todo.md) for the full checklist.

### Phase 1: Physics Engine (Tasks 1–6)
Foundation. Everything depends on this being correct.

### Phase 2: Data Generator (Tasks 7–8)
Produces the training dataset from the physics engine.

### Phase 3: ML Models (Tasks 9–11)
Trains, evaluates, and serializes all 8 models.

### Phase 4: API Layer (Tasks 12–14)
Exposes physics engine + ML models to the frontend.

### Phase 5: Frontend (Tasks 15–21)
Interactive React SPA with the "Physics Under Glass" three-layer experience.

### Phase 6: Cleanup & Polish (Tasks 22–23)
Remove legacy code, final integration, documentation.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Physics equations produce unrealistic values for edge-case geometries | High | Extensive validation tests with known textbook results; physical bounds checks on all outputs |
| DGS coupling coefficient α is empirical, may not match real antennas | Medium | Calibrate against 2-3 published DGS studies; clearly document the approximation level |
| Plotly 3D radiation surface may be slow for 181×361 grid | Medium | Offer two resolutions: low-res (91×181) for real-time updates, full-res on-demand |
| ML models overfit on physics-engine data (trivially high R²) | Low | Expected behavior — the models are learning the physics engine's function. This is fine for a demo. Document it. |
| Frontend API calls during rapid slider movement flood the backend | Medium | Debounce all API calls (300ms predict, 500ms pattern) |

## Open Questions

1. ~~Which ML models?~~ → Resolved: all 8 (Linear, Ridge, Lasso, KNN, DTree, RF, XGBoost, SVR)
2. ~~DGS slot shapes?~~ → Resolved: rectangular only (dumbbell is stretch goal)
3. Should we include a "Design Presets" dropdown (WiFi 2.4GHz, WiFi 5GHz, LTE, etc.) for quick starting points?
4. Should the frontend have an "Export Report" button (PDF of all results)?
