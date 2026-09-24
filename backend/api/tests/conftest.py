"""API pytest fixtures."""
import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.api.dependencies import load_models

@pytest.fixture(scope="session", autouse=True)
def setup_models():
    """Load models before tests."""
    # This requires models to be pre-trained at backend/data/models
    load_models()
    
@pytest.fixture
def client():
    return TestClient(app)
