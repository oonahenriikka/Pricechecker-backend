from tests.conftest import client


def test_duplicate_email_signup():
    first = client.post("/api/v1/signup", data={
        "email": "dupe@example.com",
        "password": "test123",
        "store_name": "DupeStore",
    })
    assert first.status_code == 200

    second = client.post("/api/v1/signup", data={
        "email": "dupe@example.com",
        "password": "test123",
        "store_name": "DupeStore",
    })
    assert second.status_code == 400
    assert second.json()["detail"] == "Email already registered"


def test_login_wrong_password():
    # ensure user exists
    client.post("/api/v1/signup", data={
        "email": "wrongpw@example.com",
        "password": "rightpw",
        "store_name": "WrongPWStore",
    })
    bad = client.post("/api/v1/login", data={
        "username": "wrongpw@example.com",
        "password": "wrongpw",
    })
    assert bad.status_code == 401


def test_store_duplicate_name():
    first = client.post("/api/v1/stores/", json={
        "name": "EdgeStore",
        "lat": 10.0,
        "lon": 20.0,
        "address": "Edge 1",
    })
    assert first.status_code == 200
    dup = client.post("/api/v1/stores/", json={
        "name": "EdgeStore",
        "lat": 11.0,
        "lon": 21.0,
        "address": "Edge 2",
    })
    assert dup.status_code == 400


def test_unapproved_user_cannot_add_price():
    # create store
    store_resp = client.post("/api/v1/stores/", json={
        "name": "UnapprovedStore",
        "lat": 30.0,
        "lon": 40.0,
        "address": "Addr",
    })
    assert store_resp.status_code == 200
    store_id = store_resp.json()["id"]

    # signup (not approved)
    client.post("/api/v1/signup", data={
        "email": "unapproved@example.com",
        "password": "test123",
        "store_name": "UnapprovedStore",
    })
    login = client.post("/api/v1/login", data={
        "username": "unapproved@example.com",
        "password": "test123",
    })
    assert login.status_code == 200
    token = login.json()["access_token"]

    resp = client.post(
        "/api/v1/prices",
        json={"product_name": "Edge", "price": 1.0, "store_id": store_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_missing_token_rejected():
    resp = client.post(
        "/api/v1/prices",
        json={"product_name": "NoToken", "price": 2.0, "store_id": 1},
    )
    assert resp.status_code == 401
