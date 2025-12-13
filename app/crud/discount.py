# app/crud/discount.py
from sqlalchemy.orm import Session
from app.models.discount import Discount
from app.schemas.discount import DiscountCreate

def create_discount(db: Session, discount_in: DiscountCreate, user_id: int, store_id: int):
    db_discount = Discount(**discount_in.model_dump(), created_by=user_id, store_id=store_id)
    db.add(db_discount)
    db.commit()
    db.refresh(db_discount)
    return db_discount

def get_active_discounts_for_store(db: Session, store_id: int, gtin: str = None, product_name: str = None):
    from sqlalchemy import and_, or_, func
    now = func.now()
    query = db.query(Discount).filter(
        Discount.store_id == store_id,
        Discount.valid_from <= now,
        (Discount.valid_until.is_(None) | (Discount.valid_until >= now))
    )
    if gtin:
        query = query.filter(Discount.gtin == gtin)
    elif product_name:
        query = query.filter(func.lower(Discount.product_name) == product_name.lower())
    return query.first()  # assume one active discount per product per store