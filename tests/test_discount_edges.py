from datetime import datetime, timedelta, timezone
from tests.conftest import client


def _login(email: str, password: str):
    resp = client.post(
        "/api/v1/login",
        data={"username": email, "password": password},
    )
    assert resp.status_code == 200, resp.json()
    return resp.json()["access_token"]


def _ensure_approved_user(email: str, password: str, store_name: str):
    # create store if missing
    client.post(
        "/api/v1/stores/",
        json={"name": store_name, "lat": 1.0, "lon": 1.0},
    )
    client.post(
        "/api/v1/signup",
        data={"email": email, "password": password, "store_name": store_name},
    )
    # approve
    from app.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.is_approved = True
        db.commit()
    db.close()


def _auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_discount_fixed_positive_and_negative():
    email = "discposneg@example.com"
    password = "test123"
    store = "DiscStore1"
    _ensure_approved_user(email, password, store)
    token = _login(email, password)

    # seed a price
    client.post(
        "/api/v1/prices",
        json={"product_name": "ItemA", "price": 10.0, "store_id": 1},
        headers=_auth_headers(token),
    )

    # positive fixed discount (subtract)
    pos = client.post(
        "/api/v1/discounts/",
        json={"product_name": "ItemA", "discount_fixed": 2.0},
        headers=_auth_headers(token),
    )
    assert pos.status_code == 200, pos.json()

    # negative fixed (should effectively raise price)
    neg = client.post(
        "/api/v1/discounts/",
        json={"product_name": "ItemA", "discount_fixed": -1.5},
        headers=_auth_headers(token),
    )
    assert neg.status_code == 200, neg.json()


def test_discount_validity_window():
    email = "discwindow@example.com"
    password = "test123"
    store = "DiscStore2"
    _ensure_approved_user(email, password, store)
    token = _login(email, password)

    now = datetime.now(timezone.utc)
    past = now - timedelta(days=2)
    future = now + timedelta(days=2)

    # seed price
    client.post(
        "/api/v1/prices",
        json={"product_name": "WindowItem", "price": 5.0, "store_id": 1},
        headers=_auth_headers(token),
    )

    # valid future window -> should be retrievable when within window (we set now window)
    valid = client.post(
        "/api/v1/discounts/",
        json={
            "product_name": "WindowItem",
            "discount_percent": 10.0,
            "valid_until": future.isoformat(),
        },
        headers=_auth_headers(token),
    )
    assert valid.status_code == 200, valid.json()


def test_multiple_discounts_same_product():
    email = "discdupe@example.com"
    password = "test123"
    store = "DiscStore3"
    _ensure_approved_user(email, password, store)
    token = _login(email, password)

    client.post(
        "/api/v1/prices",
        json={"product_name": "DupeItem", "price": 3.0, "store_id": 1},
        headers=_auth_headers(token),
    )

    d1 = client.post(
        "/api/v1/discounts/",
        json={"product_name": "DupeItem", "discount_percent": 5.0},
        headers=_auth_headers(token),
    )
    assert d1.status_code == 200

    d2 = client.post(
        "/api/v1/discounts/",
        json={"product_name": "DupeItem", "discount_percent": 7.0},
        headers=_auth_headers(token),
    )
    # current crud returns first match; ensure second can be created (no unique constraint)
    assert d2.status_code == 200


def test_discount_missing_store_id_invalid():
    email = "discnostore@example.com"
    password = "test123"
    store = "DiscStore4"
    _ensure_approved_user(email, password, store)
    token = _login(email, password)

    # Remove user's store to simulate invalid
    from app.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user.store_id = None
    db.commit()
    db.close()

    resp = client.post(
        "/api/v1/discounts/",
        json={"product_name": "NoStoreItem", "discount_percent": 5.0},
        headers=_auth_headers(token),
    )
    assert resp.status_code in (400, 403, 422)
