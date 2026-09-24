# Nifty 50 Trading Bot / Antenna DGS Predictor

Wait, the project was hijacked to build an Antenna DGS Predictor (Physics Under Glass)!
(As per the user rules mapping, the minor_project context became an Antenna DGS physics + ML engine).

# Antenna DGS Predictor

**Physics Under Glass** is a full-stack application that accurately predicts the resonant frequency, gain, bandwidth, and efficiency of Defected Ground Structure (DGS) microstrip patch antennas using a hybrid physics-ML engine. 

It runs physics-based Cavity Model calculations as a baseline, and layers 8 different Machine Learning models (Linear, Ridge, Lasso, KNN, Decision Tree, Random Forest, XGBoost, SVR) to capture non-linear perturbations introduced by the DGS slots.

## Architecture

1. **Frontend (Vite + React)**: 
   - A highly polished, "Physics Under Glass" dark-mode UI.
   - Real-time interactive Antenna Canvas (SVG).
   - Dynamic Radiation Pattern and S-Parameter rendering via Plotly.
   - Model comparison dashboard.
2. **Backend API (FastAPI)**:
   - High-performance API serving the ML predictions and Physics engine.
   - `lifespan` event-driven model loading from `ModelRegistry`.
3. **ML Engine (Scikit-Learn / XGBoost)**:
   - Predicts frequency shift and gain penalties based on slot dimensions.
4. **Physics Engine**:
   - Computes base cavity resonant frequency, fringing extensions, and effective dielectric constants.

## Setup Instructions

### Backend
1. Python 3.11+ is required.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Generate the dataset and train models:
   ```bash
   python -m backend.data_generator.generate --samples 10000 --seed 42
   python -m backend.ml_models.train --data backend/data/antenna_dataset.csv
   ```
5. Run the API:
   ```bash
   uvicorn backend.api.main:app --reload
   ```

### Frontend
1. Node.js 18+ is required.
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Run the development server:
   ```bash
   npm run dev
   ```

Open `http://localhost:5173` to view the application.

## Constraints & Risk Management

This project strictly adheres to constraints defined in `CONSTRAINTS.md`. All data generation is physically bounded (e.g., slots cannot overlap, inset must not exceed half patch length). No arbitrary data synthesis is allowed outside of physical validity.
