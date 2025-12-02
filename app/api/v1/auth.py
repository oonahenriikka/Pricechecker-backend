from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import create_access_token, get_password_hash, verify_password, get_current_admin_user
from app.crud.user import create_user, get_user_by_email, approve_user
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, Token, EmailStr
from app.models.user import User
from app.models.store import Store
from sqlalchemy import func

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def signup(
    email: EmailStr = Form(...),
    password: str = Form(...),
    store_name: str = Form(...),
    db: Session = Depends(get_db)
):
    store = db.query(Store).filter(func.lower(Store.name) == func.lower(store_name.strip())).first()
    if not store:
        raise HTTPException(status_code=400, detail="Store not found")
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = get_password_hash(password)
    user = create_user(db=db, email=email, password=hashed, store_id=store.id, is_admin=False)
    return user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    from app.core.security import authenticate_user  # local import to avoid circular
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user or not user.is_approved:
        raise HTTPException(status_code=401, detail="Invalid credentials or not approved")
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/approve/{user_id}")
def approve(user_id: int, admin=Depends(get_current_admin_user), db: Session = Depends(get_db)):
    user = approve_user(db, user_id)
    if not user:
        raise HTTPException(404, detail="User not found")
    return {"message": f"User {user.email} approved"}