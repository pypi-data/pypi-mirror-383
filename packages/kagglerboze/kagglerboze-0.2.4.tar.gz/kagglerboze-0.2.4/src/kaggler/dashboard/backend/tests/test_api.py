"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Kaggler Dashboard API"
    assert data["status"] == "running"


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_competitions():
    """Test listing competitions."""
    response = client.get("/api/competitions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_competition_not_found():
    """Test getting non-existent competition."""
    response = client.get("/api/competitions/invalid-id")
    assert response.status_code == 404


def test_start_competition():
    """Test starting a new competition."""
    competition_data = {
        "competition_name": "Test Competition",
        "dataset_path": "/path/to/dataset",
        "population_size": 10,
        "generations": 5,
        "objectives": ["accuracy", "complexity"],
    }
    response = client.post("/api/compete", json=competition_data)
    assert response.status_code == 200
    data = response.json()
    assert "competition_id" in data
    assert data["status"] == "running"


def test_get_system_metrics():
    """Test getting system metrics."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "cpu_usage" in data
    assert "memory_usage" in data
    assert "active_competitions" in data


@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection."""
    with client.websocket_connect("/ws/evolution") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "connected"
