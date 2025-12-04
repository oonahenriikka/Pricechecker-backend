from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_active_user
from app.crud.discount import create_discount, get_active_discounts_for_store
from app.schemas.discount import DiscountCreate, DiscountResponse
from app.models.user import User

router = APIRouter(prefix="/discounts", tags=["discounts"])

@router.post("/", response_model=DiscountResponse)
def create_store_discount(
    discount_in: DiscountCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_approved:
        raise HTTPException(403, "Not approved")
    # Optional: check that user belongs to the store
    return create_discount(db=db, discount_in=discount_in, user_id=current_user.id)