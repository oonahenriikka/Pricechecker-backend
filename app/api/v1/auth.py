from fastapi import APIRouter, Depends, HTTPException, Form, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import create_access_token, get_current_admin_user
from app.crud.user import create_user, get_user_by_email, approve_user
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, Token, EmailStr
from app.schemas.store import StoreCreate
from app.models.user import User
from app.models.store import Store
from app.crud.store import create_store
from sqlalchemy import func

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def signup(
    user_in: UserCreate | None = Body(None),  # JSON body path
    email: EmailStr | None = Form(None),
    password: str | None = Form(None),
    store_name: str | None = Form(None),
    db: Session = Depends(get_db)
):
    # Accept both JSON (UserCreate) and form data (used by tests/clients)
    if user_in:
        email = user_in.email
        password = user_in.password
        store_name = user_in.store_name
    else:
        if not all([email, password, store_name]):
            raise HTTPException(status_code=400, detail="email, password, store_name required")

    store_name_clean = store_name.strip()
    store = db.query(Store).filter(func.lower(Store.name) == func.lower(store_name_clean)).first()
    if not store:
        # Auto-create store placeholder if missing (tests assume signup works without pre-creating store)
        store = create_store(db, StoreCreate(name=store_name_clean, lat=0.0, lon=0.0, address=None))
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Pass plain password; create_user will hash internally
    user = create_user(
        db=db,
        email=email,
        password=password,
        store_id=store.id,
        is_admin=False,
    )
    return user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    from app.core.security import authenticate_user  # local import to avoid circular
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/approve/{user_id}")
def approve(user_id: int, admin=Depends(get_current_admin_user), db: Session = Depends(get_db)):
    user = approve_user(db, user_id)
    if not user:
        raise HTTPException(404, detail="User not found")
    return {"message": f"User {user.email} approved"}