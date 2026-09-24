# Statement of Intent: Antenna Performance Predictor with Defected Ground Structures

> **Status:** Confirmed  
> **Date:** 2026-09-24  
> **Source:** interview-me session  

---

## Outcome

A full-stack web application for predicting microstrip patch antenna performance with defected ground structures (DGS) — user-defined grid cut-outs on the ground plane.

The system has **three pillars**:

### Pillar 1: Physics Engine (Analytical Model)
- **Cavity model** for resonant frequency prediction (rectangular & circular patches)
- **Perturbation theory** for modeling the effect of arbitrary grid cut-outs (DGS) on resonant frequency and gain
- **Aperture theory** for gain computation
- **Full radiation pattern computation** — gain as a function of θ (theta) and φ (phi), not just scalar values
- Supports **rectangular and circular** patch geometries
- Substrate material properties (permittivity, e.g., FR4, Rogers)
- This engine serves as the **ground truth data generator** for training ML models

### Pillar 2: ML Model Comparison
- Multiple ML models trained on physics-engine-generated data:
  - Linear Regression (baseline)
  - XGBoost
  - K-Nearest Neighbors (KNN)
  - Decision Tree
  - (others as appropriate)
- **Side-by-side comparison dashboard**: for a given antenna configuration, show each model's predicted gain & frequency
- Accuracy metrics (R², MAE, RMSE) per model
- Clear identification of which model performs best

### Pillar 3: Visualization & UI
- **Interactive antenna configurator**: select patch shape (rectangular/circular), set substrate & patch dimensions, feed parameters
- **Interactive grid for cut-out placement**: user specifies 4 bounding points on a coordinate grid to define DGS regions
- **2D Polar radiation pattern**: gain (dB) vs. angle — classic HFSS-style plot with main lobe, back lobe, nulls
- **3D Radiation pattern surface**: color-mapped "balloon" plot showing rETotal magnitude across θ/φ with color scale
- **Model comparison section**: predictions from all models displayed side-by-side
- **Premium, modern aesthetic**: polished UI that impresses on first sight

---

## User
The developer, for a **3-credit university course** where **100% of the grade** depends on this project.

> ⚠️ "Minor Project" is the course name, not a scope indicator. This is a full, high-stakes academic deliverable.

---

## Why Now
The current Streamlit prototype is a placeholder demo. This is the real, graded deliverable that replaces it entirely.

---

## Success Criteria
1. The physics engine produces **defensible, physics-grounded** predictions for rectangular and circular patches with arbitrary cut-outs — must withstand academic scrutiny
2. ML models are trained, evaluated, and compared **transparently** with proper metrics
3. The UI is **premium-quality** — interactive antenna configurator, coordinate grid for cut-outs, real-time predictions, and **publication-quality radiation pattern plots** (2D polar + 3D surface)
4. The entire system is **functional**, not just pretty — predictions must be accurate and physics-based

---

## Constraints
- **No EM simulator access** (no CST Studio, HFSS, FEKO) — the analytical engine is the ceiling for data quality; it must be rigorous
- No deep learning models unless explicitly added later

---

## Out of Scope
- Keeping the existing Streamlit app or any legacy code that doesn't serve the new architecture (can be deleted)
- Deep learning models (LSTM, neural networks) unless user explicitly requests
- Full-wave EM simulation integration

---

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | Vite + React (interactive plots via Plotly/Three.js, premium UI) |
| Backend | Python FastAPI (physics engine, ML model serving, radiation pattern computation) |
| ML | Scikit-Learn, XGBoost |
| Data | NumPy, Pandas, SciPy (for physics computations) |
| Visualization | Plotly.js (2D polar), Three.js or Plotly 3D (3D radiation surface) |

---

## Key Design Decisions
- **Physics engine as ground truth**: Since we lack EM simulator data, the analytical model (cavity model + perturbation theory) IS the training data source. Its rigor directly determines ML model quality.
- **Full radiation pattern, not just scalar gain**: The physics engine must compute gain(θ, φ) across the full angular domain to generate the 2D polar and 3D surface plots.
- **Model comparison is a first-class feature**: Not hidden — users see all models' predictions side-by-side with accuracy metrics.
- **Interactive cut-out placement**: Users define DGS regions via coordinate points on a visual grid, not just numeric inputs.
