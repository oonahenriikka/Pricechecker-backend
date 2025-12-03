from sqlalchemy.orm import Session
from app.models.price import Price
from app.schemas.price import PriceCreate

def create_price(db: Session, price_in: PriceCreate, user_id: int):
    db_price = Price(
        product_name=price_in.product_name,
        price=price_in.price,
        store_id=price_in.store_id,
        user_id=user_id,
        barcode_type=price_in.barcode.barcode_type if price_in.barcode else None,
        gtin=price_in.barcode.gtin if price_in.barcode else None,
    )
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price

def get_prices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Price).offset(skip).limit(limit).all()