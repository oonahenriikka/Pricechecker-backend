from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import timedelta
from typing import List

from app.database import Base, engine, get_db, SessionLocal
from app.models.store import Store
from app.models import user, price
from app.schemas.store import StoreCreate, StoreResponse
from app.schemas.user import UserCreate, UserResponse, Token, EmailStr
from app.schemas.price import PriceCreate, PriceResponse
from app.crud.store import create_store
from app.crud.user import create_user, get_user_by_email, approve_user
from app.crud.price import create_price, get_prices
from app.auth import (
    create_access_token, authenticate_user, get_current_admin_user,
    get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.utils import get_password_hash

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Price Checker Backend",
    description="TWC 2025 – Team project",
    version="0.1.0"
)


@app.on_event("startup")
def create_first_admin():
    db: Session = SessionLocal()
    try:
        if not get_user_by_email(db, "admin@pricechecker.fi"):
            create_user(
                db=db,
                email="admin@pricechecker.fi",
                password="admin123",
                is_admin=True
            )
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Backend is running! Database ready."}


@app.post("/stores/", response_model=StoreResponse)
def api_create_store(store: StoreCreate, db: Session = Depends(get_db)):
    existing = db.query(Store).filter(Store.name == store.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Store with this name already exists")
    return create_store(db=db, store=store)


@app.post("/signup", response_model=UserResponse)
def signup(
    email: EmailStr = Form(...),
    password: str = Form(...),
    store_name: str = Form(...),
    db: Session = Depends(get_db)
):

    store = db.query(Store).filter(
        func.lower(Store.name) == func.lower(store_name.strip())
    ).first()
    if not store:
        raise HTTPException(
            status_code=400,
            detail="Store not found. Please check the exact name (case-insensitive)."
        )


    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")

  
    hashed_password = get_password_hash(password)
    new_user = create_user(
        db=db,
        email=email,
        password=hashed_password,
        store_id=store.id,
        is_admin=False
    )
    return new_user


@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user or not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password or not approved yet"
        )
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/admin/approve/{user_id}")
def approve_user_endpoint(
    user_id: int,
    admin=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    user = approve_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {user.email} approved"}


@app.post("/prices/", response_model=PriceResponse)
def add_price(
    price_in: PriceCreate,
    current_user: user.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_approved:
        raise HTTPException(status_code=403, detail="Only approved store users can add prices")
    return create_price(
        db=db,
        product_name=price_in.product_name,
        price=price_in.price,
        store_id=price_in.store_id,
        user_id=current_user.id
    )


@app.get("/prices/", response_model=List[PriceResponse])
def list_prices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_prices(db, skip, limit)