from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, Base, engine
from app.crud.user import create_user

client = TestClient(app)

def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        create_user(
            db=db,
            email="admin@pricechecker.fi",
            password="admin123",
            is_admin=True
        )
    finally:
        db.close()

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Backend is running! Database ready."}

def test_create_store():
    setup_db()
    response = client.post("/stores/", json={
        "name": "S-Market Ruoholahti",
        "latitude": 60.1626,
        "longitude": 24.9125
    })
    assert response.status_code == 200
    assert response.json()["name"] == "S-Market Ruoholahti"

def test_signup_and_login():
    setup_db()
   
    client.post("/stores/", json={
        "name": "K-Market Kamppi UNIQUE TEST",
        "latitude": 60.1699,
        "longitude": 24.9332
    })


    response = client.post("/signup", data={
        "email": "kmarket@example.com",
        "password": "store123",
        "store_name": "K-Market Kamppi UNIQUE TEST"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "kmarket@example.com"
    assert response.json()["is_approved"] is False

  
    admin_login = client.post("/login", data={
        "username": "admin@pricechecker.fi",
        "password": "admin123"
    })
    assert admin_login.status_code == 200
    token = admin_login.json()["access_token"]

 
    approve = client.post("/admin/approve/2", headers={"Authorization": f"Bearer {token}"})
    assert approve.status_code == 200

   
    store_login = client.post("/login", data={
        "username": "kmarket@example.com",
        "password": "store123"
    })
    assert store_login.status_code == 200
    store_token = store_login.json()["access_token"]

   
    price_resp = client.post("/prices/", json={
        "product_name": "Milk 1L",
        "price": 1.29,
        "store_id": 1
    }, headers={"Authorization": f"Bearer {store_token}"})
    assert price_resp.status_code == 200

   
    prices = client.get("/prices/")
    assert prices.status_code == 200
    assert len(prices.json()) >= 1