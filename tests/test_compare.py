from tests.conftest import client
from app.database import SessionLocal
from app.models.user import User

def test_compare_with_labeling(approved_store_token):
    headers = {"Authorization": f"Bearer {approved_store_token}"}

    db = SessionLocal()
    store_id = db.query(User).filter(User.email == "store@test.fi").first().store_id
    db.close()

    # Add prices to multiple stores
    client.post("/api/v1/prices/", json={
        "product_name": "Coca Cola 1.5L", "price": 2.50, "store_id": store_id
    }, headers=headers)

    resp = client.get("/api/v1/compare", params={
        "product_name": "Coca Cola 1.5L",
        "lat": 60.17,
        "lon": 24.94,
        "radius_km": 20
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["results"]) > 0
    assert "price_label" in data["results"][0]
    assert data["results"][0]["price_label"] in [
        "very inexpensive", "inexpensive", "average", "expensive", "very expensive"
    ]