from tests.conftest import client

def test_create_and_apply_discount(approved_store_token):
    headers = {"Authorization": f"Bearer {approved_store_token}"}

    discount = client.post("/api/v1/discounts/", json={
        "product_name": "Fazer Blue 200g",
        "discount_percent": 20.0
    }, headers=headers)
    assert discount.status_code == 200

    # Check it appears in compare
    resp = client.get("/api/v1/compare", params={
        "product_name": "Fazer Blue 200g",
        "lat": 60.1699,
        "lon": 24.9332
    })
    assert resp.status_code == 200
    result = resp.json()["results"][0]
    assert result["final_price"] < result["price"]
    assert "off (app only!)" in result["discount_info"]