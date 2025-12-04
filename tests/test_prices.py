from tests.conftest import client

def test_add_price_batch(approved_store_token):
    headers = {"Authorization": f"Bearer {approved_store_token}"}

    # Single price
    resp = client.post("/api/v1/prices/", json={
        "product_name": "Fazer Blue 200g",
        "price": 2.49,
        "store_id": 1,
        "barcode": {"barcode_type": "EAN13", "gtin": "6416453015174"}
    }, headers=headers)
    assert resp.status_code == 200

    # Batch upload
    csv_content = """
product_name,price,store_id,barcode_type,gtin
Maitosuklaa,1.99,1,EAN13,6416453015181
Ruisleipä,2.10,1,EAN13,6416453015198
    """.strip()

    files = {"file": ("prices.csv", csv_content, "text/csv")}
    batch = client.post("/api/v1/prices/batch", files=files, headers=headers)
    assert batch.status_code == 200
    assert batch.json()["success_count"] >= 2