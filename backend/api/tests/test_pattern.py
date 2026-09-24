"""Tests for pattern and S-parameter endpoints."""
from fastapi.testclient import TestClient

def test_pattern(client: TestClient) -> None:
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
    
    response = client.post("/api/pattern?resolution_deg=10", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "theta" in data
    assert "phi" in data
    assert "gain_db" in data
    assert "e_plane" in data
    
    # Check shapes
    # theta: 0 to 90 step 10 -> 10 points
    # phi: 0 to 360 step 10 -> 37 points
    assert len(data["theta"]) == 10
    assert len(data["phi"]) == 37
    assert len(data["gain_db"]) == 10
    assert len(data["gain_db"][0]) == 37


def test_s_parameter(client: TestClient) -> None:
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
    
    response = client.post("/api/s-parameter?points=51&span_ghz=0.5", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "freq_ghz" in data
    assert "s11_db" in data
    assert len(data["freq_ghz"]) == 51
    assert len(data["s11_db"]) == 51
    
    # The minimum S11 should be somewhere in the middle
    min_s11 = min(data["s11_db"])
    assert min_s11 < -10.0 # Should have a resonance dip
