from sqlalchemy.orm import Session
from app.models.price import Price

def create_price(db: Session, product_name: str, price: float, store_id: int, user_id: int):
    db_price = Price(
        product_name=product_name,
        price=price,
        store_id=store_id,
        user_id=user_id
    )
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price

def get_prices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Price).offset(skip).limit(limit).all()