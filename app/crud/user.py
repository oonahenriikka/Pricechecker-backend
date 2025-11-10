from sqlalchemy.orm import Session
from app.models.user import User
from app.utils import get_password_hash

def create_user(db: Session, email: str, password: str, is_admin: bool = False, store_name: str = None):
    hashed = get_password_hash(password)
    user = User(
        email=email,
        hashed_password=hashed,
        is_admin=is_admin,
        is_approved=True if is_admin else False,
        store_name=store_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first

def approve_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_approved = True
        db.commit()
        db.refresh(user)
    return user