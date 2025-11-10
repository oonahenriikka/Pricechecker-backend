from sqlalchemy.orm import Session
from app.models.store import Store
from app.schemas.store import StoreCreate

def create_store(db: Session, store: StoreCreate):
    db_store = Store(**store.model_dump())
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store