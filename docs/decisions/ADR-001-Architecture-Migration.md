# ADR-001: Architecture Migration - From Streamlit/Sklearn to FastAPI/React

## Status
Accepted

## Date
2026-09-25

## Context
The Antenna DGS Predictor was originally conceived as a series of isolated Python scripts (`simulate_data.py`, `forward_model.py`, `inverse_model.py`, `data_processor.py`) alongside a basic Streamlit UI. While functional for early prototyping, this monolithic architecture presented significant limitations:
- **Coupled Logic:** Data generation, ML inference, and physical calculations were heavily intertwined without a clear boundary.
- **UI Constraints:** Streamlit is excellent for data science but lacks the rich interactivity, local rendering speeds, and aesthetic customizability required for our "Physics Under Glass" vision (e.g., dynamic SVG canvases, debounced sliders, Plotly 3D surfaces).
- **Maintenance Cost:** We carried a heavy load of "zombie code" (like `benchmark.py`, `benchmark_sk.py`, etc.) that were no longer maintained and lacked typing, making future physical constraint validation extremely error-prone.

## Decision
We decided to deprecate the legacy monolithic python scripts and adopt a modern, decoupled architecture:
1. **Frontend:** React 18, Vite, TypeScript, and Plotly.js (`react-plotly.js`).
2. **Backend:** FastAPI for a typed, high-performance API boundary using Pydantic.
3. **Physics/ML Separation:** Strict decoupling in the backend between the Physics Engine (`backend/physics_engine`) and Machine Learning pipeline (`backend/ml_models`).

## Alternatives Considered

### Retaining Streamlit and refactoring the backend
- **Pros:** Less immediate rewrites; Python-only ecosystem.
- **Cons:** We still wouldn't be able to achieve the interactive, 60fps design system requested (Canvas rendering, debouncing). Streamlit redraws the entire UI state on the server upon every interaction.
- **Rejected:** The UX constraint of a responsive "Physics Under Glass" UI made a browser-native frontend mandatory.

### Adopting Next.js instead of Vite + React (SPA)
- **Pros:** SSR capabilities, full-stack unified repo.
- **Cons:** Our backend is heavily reliant on the Python Scientific stack (numpy, scipy, scikit-learn, xgboost). Moving to Next.js would require us to either rewrite the physics engine in TypeScript or maintain a Next.js server that just proxies to a Python server.
- **Rejected:** Since we absolutely require Python for the physics and ML models, a dedicated Python backend API paired with a lightweight, fast SPA Vite frontend was the cleanest architectural boundary.

## Consequences
- We successfully deprecated and removed the legacy Python files (`simulate_data.py`, `forward_model.py`, etc.).
- We must maintain separate CI/CD quality gates for Frontend (npm/vitest/eslint) and Backend (pytest/pip). This has been automated via GitHub actions.
- The UI is significantly more responsive, with zero-latency visual rendering of the antenna patch dimensions, backed by heavily optimized threadpool FastAPI endpoints.
