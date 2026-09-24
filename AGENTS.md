# Project: Antenna DGS Predictor (Physics Under Glass)

Read `CONSTRAINTS.md` before writing code. Do not weaken it to make a change pass.

## Tech Stack
- **Frontend**: React 18, Vite, TypeScript, Plotly.js (`react-plotly.js`)
- **Backend**: Python 3.11, FastAPI, Uvicorn, Scikit-Learn, XGBoost, Pandas, NumPy
- **Physics**: Custom Cavity Model implementation (local math)

## Commands
- **Frontend Dev**: `npm run dev` (in `frontend/`)
- **Frontend Test**: `npx vitest run` (in `frontend/`)
- **Frontend Build**: `npm run build` (in `frontend/`)
- **Backend API**: `uvicorn backend.api.main:app --reload` (in root)
- **Backend Test**: `pytest backend/ -v` (in root)
- **Generate Data**: `python -m backend.data_generator.generate --samples 10000 --seed 42 --output backend/data/antenna_dataset.csv`
- **Train Models**: `python -m backend.ml_models.train --data backend/data/antenna_dataset.csv`

## Code Conventions (Frontend)
- Use functional React components with hooks.
- Use `GlassCard` wrapper for standard UI panel aesthetics.
- Animations and transitions must follow the Physics Under Glass aesthetic (dark mode, glassmorphism, glowing accents).
- Strictly adhere to `verbatimModuleSyntax` (e.g. `import type { AntennaConfig }`).
- Co-locate tests in `src/test/` using Vitest and React Testing Library (`jsdom`).

## Code Conventions (Backend)
- Use Pydantic models for request/response serialization.
- Separate routing (`api/routes`) from business/physics logic (`physics_engine`).
- Data manipulation must use vectorized Pandas/NumPy operations; avoid `iterrows`.
- Machine Learning pipelines must serialize artifacts to `backend/ml_models/saved_models/*.joblib`.

## Boundaries & Risk Guardrails
- **Physics Validity**: Synthesized data must never exceed physical limits (e.g., feed inset > patch length/2 is invalid).
- **Security**: Use `.env` for secrets, and never check them into git (enforced by `.gitignore`).
- Never overwrite the generated ML models with untargeted code without running `pytest` first.

## File Organization
- `backend/api`: FastAPI application
- `backend/physics_engine`: Antenna cavity equations
- `backend/ml_models`: Training scripts and model registry
- `backend/data_generator`: Data synthesis for ML training
- `frontend/src`: Vite React frontend
