from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_active_user
from app.crud.price import create_price, get_prices
from app.schemas.price import PriceCreate, PriceResponse
from app.models.user import User

router = APIRouter()

@router.post("/prices", response_model=PriceResponse)
def add_price(
    price_in: PriceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_approved:
        raise HTTPException(403, detail="Not approved")
    return create_price(db=db, price_in=price_in, user_id=current_user.id)

@router.get("/prices", response_model=List[PriceResponse])
def list_prices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_prices(db, skip=skip, limit=limit)