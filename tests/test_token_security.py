from datetime import datetime, timedelta, timezone
from jose import jwt
from tests.conftest import client
from app.core.security import ALGORITHM, SECRET_KEY
from app.database import SessionLocal
from app.models.user import User


def _get_store_id(email: str) -> int:
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        db.close()
        raise AssertionError("Expected user to exist")
    store_id = user.store_id
    db.close()
    return store_id


def test_expired_token_rejected(approved_store_token):
    email = "store@test.fi"
    store_id = _get_store_id(email)
    expired_token = jwt.encode(
        {"sub": email, "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    resp = client.post(
        "/api/v1/prices",
        json={"product_name": "Expired", "price": 1.0, "store_id": store_id},
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp.status_code == 401


def test_invalid_signature_token(approved_store_token):
    email = "store@test.fi"
    store_id = _get_store_id(email)
    bad_secret = SECRET_KEY + "-tampered"
    tampered = jwt.encode(
        {"sub": email, "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        bad_secret,
        algorithm=ALGORITHM,
    )
    resp = client.post(
        "/api/v1/prices",
        json={"product_name": "Tampered", "price": 2.0, "store_id": store_id},
        headers={"Authorization": f"Bearer {tampered}"},
    )
    assert resp.status_code == 401
