# How to Run (For Forked Repositories)

Welcome to the **Antenna DGS Predictor (Physics Under Glass)** project! If you've just forked this repository from GitHub, follow these step-by-step instructions to get the full-stack application running on your local machine.

## Prerequisites

Ensure you have the following installed on your system:
- **Git**
- **Python 3.11+** (for the backend API and ML engine)
- **Node.js 18+** (for the frontend Vite/React app)

---

## 1. Clone Your Fork

First, clone your forked repository to your local machine:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_FORK_NAME.git
cd YOUR_FORK_NAME
```

*(Replace `YOUR_USERNAME` and `YOUR_FORK_NAME` with your actual GitHub details).*

---

## 2. Set Up the Backend & ML Engine

The backend is built with FastAPI, Scikit-Learn, and XGBoost. It serves the ML predictions and physics engine calculations.

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - On **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
   - On **Windows**:
     ```bash
     venv\Scripts\activate
     ```

3. **Install dependencies:**
   Make sure you are at the root of the project and install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate the synthetic dataset:**
   The ML models require training data. Generate the synthetic dataset (this guarantees data falls within valid physical boundaries):
   ```bash
   python -m backend.data_generator.generate --samples 10000 --seed 42 --output backend/data/antenna_dataset.csv
   ```

5. **Train the Machine Learning models:**
   Run the training pipeline to build and serialize the models:
   ```bash
   python -m backend.ml_models.train --data backend/data/antenna_dataset.csv
   ```

6. **Start the FastAPI Backend Server:**
   Run the backend API using Uvicorn:
   ```bash
   uvicorn backend.api.main:app --reload
   ```
   *(If you get an `[Errno 48] Address already in use` error, it means another process is using port 8000. Start it on a different port instead:)*
   ```bash
   uvicorn backend.api.main:app --reload --port 8001
   ```
   *The backend will now be running at `http://127.0.0.1:8000` (or your custom port). You can view the API documentation at `http://127.0.0.1:8000/docs`. Keep this terminal window open.*

---

## 3. Set Up the Frontend

The frontend is a Vite + React application with a highly polished "Physics Under Glass" UI.

1. **Open a new terminal window** (keep the backend running in the previous one).

2. **Navigate to the frontend directory and start the server:**
   *Important: You must be inside the `frontend` folder before running these commands!*
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **View the Application:**
   Open your browser and navigate to the local URL provided by Vite (typically `http://localhost:5173`).

---

## 4. Running Tests

To ensure everything is working correctly after forking, you can run the provided test suites:

- **Backend Tests:**
  From the root directory with your virtual environment activated:
  ```bash
  pytest backend/ -v
  ```

- **Frontend Tests:**
  From the `frontend/` directory:
  ```bash
  npx vitest run
  ```

---

## Important Notes for Contributors

- **Constraints:** Please review `CONSTRAINTS.md` before making changes. It outlines the physical boundaries for data generation and strict project guardrails (e.g. feed inset > patch length/2 is invalid).
- **Frontend Architecture:** Ensure you use functional React components with hooks. The UI strictly follows a dark-mode glassmorphism aesthetic using standard `GlassCard` wrappers.
- **Backend Architecture:** Routing logic (`api/routes`) is strictly separated from the core physics calculations (`physics_engine`). Please maintain this separation.
