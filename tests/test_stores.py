from tests.conftest import client

def test_create_and_list_stores(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Create store
    resp = client.post("/api/v1/stores/", json={
        "name": "Prisma Itäkeskus",
        "lat": 60.2111,
        "lon": 25.0829,
        "address": "Itäkatu 1"
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Prisma Itäkeskus"

    # List stores
    all_stores = client.get("/api/v1/stores/")
    assert all_stores.status_code == 200
    assert len(all_stores.json()) > 0

# Get store by ID
def test_get_store_by_id(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    create = client.post("/api/v1/stores/", json={
        "name": "S-market Majakkaranta",
        "lat": 60.4296,
        "lon": 22.2394,
        "address": "Kölikatu 2"
    }, headers=headers)

    store_id = create.json()["id"]

    resp = client.get(f"/api/v1/stores/{store_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == store_id
    assert resp.json()["name"] == "S-market Majakkaranta"

# Delete store by ID
def test_delete_store_by_id(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}    
    store = client.post("/api/v1/stores/", json={
        "name": "S-market Majakkaranta",
        "lat": 60.4296,
        "lon": 22.2394,
        "address": "Kölikatu 2"
    }, headers=headers).json()

    resp = client.delete(f"/api/v1/stores/{store['id']}", headers=headers)
    assert resp.status_code == 204


# Search nearby stores
def test_nearby_stores(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get("/api/v1/stores/nearby", params={
        "lat": 60.4503,
        "lon": 22.2957, #TUAS address
        "radius": 0.02 # 2.22km
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()  
    assert isinstance(data, list)