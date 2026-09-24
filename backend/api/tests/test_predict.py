"""Tests for API routes."""
from fastapi.testclient import TestClient

def test_health(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["models_loaded"] == 8

def test_predict_valid(client: TestClient) -> None:
    payload = {
        "substrate": {
            "epsilon_r": 4.4,
            "tan_delta": 0.02,
            "height_mm": 1.6,
            "width_mm": 60.0,
            "length_mm": 60.0
        },
        "patch": {
            "width_mm": 38.0,
            "length_mm": 29.0
        },
        "feed": {
            "width_mm": 3.0,
            "inset_mm": 8.0
        },
        "slots": []
    }
    
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Check physics
    assert "physics" in data
    assert "eps_eff" in data["physics"]
    assert "l_eff_meters" in data["physics"]
    
    # Check ML predictions
    assert "ml_predictions" in data
    assert "xgboost" in data["ml_predictions"]
    assert "resonant_frequency_hz" in data["ml_predictions"]["xgboost"]


def test_predict_invalid_physics(client: TestClient) -> None:
    # Patch wider than substrate
    payload = {
        "substrate": {
            "epsilon_r": 4.4,
            "tan_delta": 0.02,
            "height_mm": 1.6,
            "width_mm": 30.0,
            "length_mm": 60.0
        },
        "patch": {
            "width_mm": 38.0,
            "length_mm": 29.0
        },
        "feed": {
            "width_mm": 3.0,
            "inset_mm": 8.0
        },
        "slots": []
    }
    
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 422
    assert "Patch width cannot exceed substrate width" in response.text
