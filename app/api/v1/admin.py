from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_admin_user
from app.core.audit import log_admin_action
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

    old_status = user.is_active
    user.is_active = data.is_active
    db.commit()
    db.refresh(user)


    log_admin_action(
        db=db,
        admin_id=admin.id,
        action="user_locked" if not data.is_active else "user_unlocked",
        target_user_id=user_id,
        details={
            "old_active": old_status,
            "new_active": data.is_active,
            "performed_by": admin.email
        }
    )

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
        raise HTTPException(403, "Cannot delete admin user")

    # Save user info before deletion
    deleted_email = user.email

    db.delete(user)
    db.commit()


    log_admin_action(
        db=db,
        admin_id=admin.id,
        action="user_deleted",
        target_user_id=user_id,
        details={
            "deleted_email": deleted_email,
            "performed_by": admin.email
        }
    )

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

    old_status = user.is_admin
    user.is_admin = data.make_admin
    db.commit()
    db.refresh(user)

    
    log_admin_action(
        db=db,
        admin_id=admin.id,
        action="user_promoted_to_admin" if data.make_admin else "user_removed_from_admin",
        target_user_id=user_id,
        details={
            "old_admin": old_status,
            "new_admin": data.make_admin,
            "target_email": user.email,
            "performed_by": admin.email
        }
    )

    return user