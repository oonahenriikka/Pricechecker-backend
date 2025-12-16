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

#get 1 store by id
@router.get("/stores/{store_id}", response_model=StoreResponse)
def get_store(store_id: int, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(404, detail="Store not found")
    return store  

#delete store by id
@router.delete("/{store_id}", summary="Delete store")
def delete_store(store_id: int, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    db.delete(store)
    db.commit()

    return {"message": f"Store {store_id} deleted successfully"}
