from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models.store import Store
from app.models import user
from app.schemas.store import StoreCreate, StoreResponse
from app.schemas.user import UserCreate, UserResponse, Token
from app.crud.store import create_store
from app.crud.user import create_user, get_user_by_email, approve_user
from app.auth import (
    create_access_token, authenticate_user, get_current_admin_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Price Checker Backend",
    description="TWC 2025 – Team project",
    version="0.1.0"
)

# Auto-create first admin
@app.on_event("startup")
def create_first_admin(db: Session = Depends(get_db)):
    if not get_user_by_email(db, "admin@pricechecker.fi"):
        create_user(
            db=db,
            email="admin@pricechecker.fi",
            password="admin123",
            is_admin=True
        )

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
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(
        db=db,
        email=user_in.email,
        password=user_in.password,
        store_name=user_in.store_name
    )

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
def approve_user_endpoint(user_id: int, admin=Depends(get_current_admin_user), db: Session = Depends(get_db)):
    user = approve_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {user.email} approved"}