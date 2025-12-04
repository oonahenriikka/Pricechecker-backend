from tests.conftest import client

def test_admin_actions(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # List users
    users = client.get("/api/v1/admin/users", headers=headers)
    assert users.status_code == 200

    # Toggle active
    resp = client.patch("/api/v1/admin/users/2/active", json={"is_active": False}, headers=headers)
    assert resp.status_code == 200

    # Make admin
    resp = client.patch("/api/v1/admin/users/2/admin", json={"make_admin": True}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["is_admin"] is True

    # Delete (won't delete admin, but will 403)
    resp = client.delete("/api/v1/admin/users/1", headers=headers)
    assert resp.status_code == 403