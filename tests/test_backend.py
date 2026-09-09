# tests/test_backend.py

"""Basic tests for the FastAPI backend of ReSearchAI."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ReSearchAI API"}


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_research_endpoint_schema():
    payload = {
        "topic": "Artificial Intelligence",
        "experience_level": "beginner",
        "interest": "machine learning",
    }
    response = client.post("/research", json=payload)
    assert response.status_code == 200
    data = response.json()
    # The response should contain a status field.
    assert "status" in data
    assert data["status"] == "success"
