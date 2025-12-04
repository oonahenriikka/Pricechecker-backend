import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.crud.user import create_user

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture
def admin_token():
    db = SessionLocal()
    admin = db.query(__import__("app.models.user").user.User).filter_by(email="admin@test.fi").first()
    if not admin:
        create_user(db=db, email="admin@test.fi", password="admin123", is_admin=True, is_approved=True)
    db.close()

    login = client.post("/api/v1/login", data={"username": "admin@test.fi", "password": "admin123"})
    return login.json()["access_token"]

@pytest.fixture
def approved_store_token():
    # Create store via API (now works!)
    client.post("/api/v1/stores/", json={
        "name": "Testikauppa Oy",
        "lat": 60.1699,
        "lon": 24.9332,
        "address": "Testikatu 1"
    })

    # Signup
    client.post("/api/v1/signup", json={
        "email": "store@test.fi",
        "password": "store123",
        "store_name": "Testikauppa Oy"
    })

    # Approve via DB
    db = SessionLocal()
    from app.models.user import User
    user = db.query(User).filter(User.email == "store@test.fi").first()
    if user:
        user.is_approved = True
        db.commit()
    db.close()

    login = client.post("/api/v1/login", data={"username": "store@test.fi", "password": "store123"})
    return login.json()["access_token"]