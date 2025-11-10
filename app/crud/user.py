from sqlalchemy.orm import Session
from app.models.user import User
from app.models.store import Store
from app.utils import get_password_hash
from sqlalchemy import func


def create_user(
    db: Session,
    email: str,
    password: str,
    store_id: int | None = None,
    is_admin: bool = False
):
    """
    Create a new user.
    - If store_id is provided → store user
    - If is_admin=True → auto-approved admin
    """
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        hashed_password=hashed_password,
        store_id=store_id,
        is_admin=is_admin,
        is_approved=is_admin  
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def approve_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_approved = True
        db.commit()
        db.refresh(user)
    return user