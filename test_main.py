from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Backend is running! Database ready."}

def test_create_store():
    payload = {
        "name": "S-Market Ruoholahti",
        "latitude": 60.1626,
        "longitude": 24.9125
    }
    response = client.post("/stores/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["id"] is not None
    assert abs(data["latitude"] - 60.1626) < 0.0001
    assert abs(data["longitude"] - 24.9125) < 0.0001

def test_create_duplicate_store():
    payload = {
        "name": "S-Market Ruoholahti",
        "latitude": 60.0,
        "longitude": 25.0
    }
    response = client.post("/stores/", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]