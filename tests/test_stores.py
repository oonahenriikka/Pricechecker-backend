from tests.conftest import client

def test_create_and_list_stores(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = client.post("/api/v1/stores/", json={
        "name": "Prisma Itäkeskus",
        "lat": 60.2111,
        "lon": 25.0829,
        "address": "Itäkatu 1"
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Prisma Itäkeskus"

    all_stores = client.get("/api/v1/stores/")
    assert all_stores.status_code == 200
    assert len(all_stores.json()) > 0