import pytest
from fastapi.testclient import TestClient
from main import app
from core.database import init_db

init_db()
client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_scan_invalid_domain():
    response = client.post("/api/scans", json={"domain": "invalid_domain.com!"})
    assert response.status_code == 400
    assert "Invalid domain format" in response.json()["detail"]

def test_dashboard_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "scans" in data
    assert "subdomains" in data
