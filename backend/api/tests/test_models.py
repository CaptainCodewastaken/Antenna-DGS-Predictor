"""Tests for model and DGS endpoints."""
from fastapi.testclient import TestClient

def test_models_compare(client: TestClient) -> None:
    response = client.get("/api/models/compare")
    assert response.status_code == 200
    data = response.json()
    assert "xgboost" in data
    assert "r2" in data["xgboost"]["resonant_frequency_hz"]

def test_models_feature_importance(client: TestClient) -> None:
    response = client.get("/api/models/feature-importance")
    assert response.status_code == 200
    data = response.json()
    assert "xgboost" in data
    assert "patch_l" in data["xgboost"]["resonant_frequency_hz"]

def test_models_learning_curves(client: TestClient) -> None:
    response = client.get("/api/models/learning-curves")
    assert response.status_code == 200
    data = response.json()
    assert "xgboost" in data
    assert "train_sizes" in data["xgboost"]["resonant_frequency_hz"]

def test_dgs_circuit(client: TestClient) -> None:
    payload = {
        "width_mm": 5.0,
        "length_mm": 15.0,
        "x_mm": 0.0,
        "y_mm": 10.0
    }
    response = client.post("/api/dgs/circuit?substrate_height_mm=1.6&epsilon_r=4.4", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "L_nH" in data
    assert "C_pF" in data
    assert "f_resonant_ghz" in data
    assert data["L_nH"] > 0
