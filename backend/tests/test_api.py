from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_predict_valid():
    with TestClient(app) as client:
        payload = {
            "substrate": {
                "epsilon_r": 4.4,
                "tan_delta": 0.02,
                "height_mm": 1.6,
                "width_mm": 60,
                "length_mm": 60
            },
            "patch": {
                "width_mm": 40,
                "length_mm": 30
            },
            "feed": {
                "width_mm": 3,
                "inset_mm": 10
            },
            "slots": []
        }
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "physics" in data
        assert "ml_predictions" in data
        assert "radiation_efficiency" in data["physics"]

def test_predict_invalid_patch_size():
    with TestClient(app) as client:
        payload = {
            "substrate": {
                "epsilon_r": 4.4,
                "tan_delta": 0.02,
                "height_mm": 1.6,
                "width_mm": 20,
                "length_mm": 20
            },
            "patch": {
                "width_mm": 40,
                "length_mm": 30
            },
            "feed": {
                "width_mm": 3,
                "inset_mm": 10
            },
            "slots": []
        }
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 422 # Patch cannot exceed substrate
