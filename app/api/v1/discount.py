from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.core.security import get_current_active_user
from app.crud.discount import create_discount, get_active_discounts_for_store
from app.crud.price import create_price
from app.schemas.discount import DiscountCreate, DiscountResponse
from app.schemas.price import PriceCreate
from app.models.user import User
from app.models.price import Price

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
    created = create_discount(
        db=db,
        discount_in=discount_in,
        user_id=current_user.id,
        store_id=current_user.store_id,
    )

    # Ensure there is at least one price entry so compare endpoint can surface the discount
    existing_price = (
        db.query(Price)
        .filter(Price.store_id == current_user.store_id)
        .filter(func.lower(Price.product_name) == discount_in.product_name.lower())
        .first()
    ) if discount_in.product_name else None

    if discount_in.product_name and not existing_price:
        create_price(
            db=db,
            price_in=PriceCreate(
                product_name=discount_in.product_name,
                price=1.0,
                store_id=current_user.store_id,
                barcode=None,
            ),
            user_id=current_user.id,
        )
        db.commit()

    return created