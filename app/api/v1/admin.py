from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_admin_user
from app.models.user import User as DBUser
from app.schemas.user import UserAdminResponse, UserToggleActive, UserMakeAdmin
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=list[UserAdminResponse])
def list_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    return db.query(DBUser).all()

@router.patch("/users/{user_id}/active", response_model=UserAdminResponse)
def toggle_user_active(
    user_id: int,
    data: UserToggleActive,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    if user.is_admin and user.id != admin.id:
        raise HTTPException(403, "Cannot modify another admin")
    user.is_active = data.is_active
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    if user.is_admin:
        raise HTTPException(403, "Cannot delete admin")
    db.delete(user)
    db.commit()
    return None

@router.patch("/users/{user_id}/admin", response_model=UserAdminResponse)
def make_admin(
    user_id: int,
    data: UserMakeAdmin,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    user.is_admin = data.make_admin
    db.commit()
    db.refresh(user)
    return user