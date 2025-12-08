# tests/test_auth.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_signup_login():
    # Clean signup (using Form data, not JSON)
    response = client.post("/api/v1/signup", data={
        "email": "user@example.com",
        "password": "test123",
        "store_name": "Lidl Test"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"
    assert response.json()["is_approved"] is False

    login = client.post("/api/v1/login", data={
        "username": "user@example.com",
        "password": "test123"
    })
    assert login.status_code == 200
    assert "access_token" in login.json()