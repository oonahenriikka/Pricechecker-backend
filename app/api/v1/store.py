from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.store import create_store
from app.schemas.store import StoreCreate, StoreResponse
from app.models.store import Store

router = APIRouter()

@router.post("/stores", response_model=StoreResponse)
def create_new_store(store: StoreCreate, db: Session = Depends(get_db)):
    existing = db.query(Store).filter(Store.name == store.name).first()
    if existing:
        raise HTTPException(400, detail="Store already exists")
    return create_store(db=db, store=store)


@router.get("/stores", response_model=list[StoreResponse])
def list_stores(db: Session = Depends(get_db)):
    return db.query(Store).all()