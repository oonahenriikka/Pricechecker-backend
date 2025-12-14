from tests.conftest import client

def test_compare_404_when_not_found():
    resp = client.get(
        "/api/v1/compare",
        params={"product_name": "NonExisting", "lat": 0, "lon": 0, "radius_km": 10},
    )
    assert resp.status_code == 404


def test_compare_filters_by_radius():
    # store A near (0,0)
    store_a = client.post("/api/v1/stores/", json={"name": "RadiusA", "lat": 0.0, "lon": 0.0}).json()
    store_b = client.post("/api/v1/stores/", json={"name": "RadiusB", "lat": 80.0, "lon": 80.0}).json()

    from app.database import SessionLocal
    from app.crud.user import create_user
    from app.crud.price import create_price
    from app.schemas.price import PriceCreate

    db = SessionLocal()
    user = create_user(db, email="radius@test", password="pw", store_id=store_a["id"], is_admin=True)
    create_price(db, PriceCreate(product_name="RadItem", price=1.0, store_id=store_a["id"], barcode=None), user.id)
    create_price(db, PriceCreate(product_name="RadItem", price=2.0, store_id=store_b["id"], barcode=None), user.id)
    db.close()

    resp = client.get(
        "/api/v1/compare",
        params={"product_name": "RadItem", "lat": 0, "lon": 0, "radius_km": 50},
    )
    assert resp.status_code == 200
    data = resp.json()
    # Only store A should be within 50km
    assert all(item["store_name"] == "RadiusA" for item in data["results"])


def test_compare_prefers_gtin_match_over_name():
    store = client.post("/api/v1/stores/", json={"name": "GtinStore", "lat": 10.0, "lon": 10.0}).json()
    from app.database import SessionLocal
    from app.crud.user import create_user
    from app.schemas.price import PriceCreate
    from app.crud.price import create_price

    db = SessionLocal()
    user = create_user(db, email="gtin@test", password="pw", store_id=store["id"], is_admin=True)
    create_price(
        db,
        PriceCreate(product_name="Milk", price=3.0, store_id=store["id"], barcode={"barcode_type": "EAN13", "gtin": "123"}),
        user.id,
    )
    db.close()

    token = client.post("/api/v1/login", data={"username": "gtin@test", "password": "pw"}).json()["access_token"]
    client.post(
        "/api/v1/discounts/",
        json={"gtin": "123", "discount_percent": 10.0},
        headers={"Authorization": f"Bearer {token}"},
    )

    resp = client.get(
        "/api/v1/compare",
        params={"product_name": "Milk", "lat": 10.0, "lon": 10.0, "radius_km": 200},
    )
    assert resp.status_code == 200, resp.json()
    res = resp.json()["results"][0]
    assert res["discount_info"] is not None
    assert res["gtin"] == "123"


def test_compare_invalid_params():
    bad = client.get("/api/v1/compare", params={"product_name": "", "lat": "NaN", "lon": 0})
    assert bad.status_code in (400, 422, 404)
