from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models.store import Store 
from app.schemas.store import StoreCreate, StoreResponse
from app.crud.store import create_store

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Price Checker Backend",
    description="TWC 2025 – Team project",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message": "Backend is running! Database ready."}

@app.post("/stores/", response_model=StoreResponse)
def api_create_store(store: StoreCreate, db: Session = Depends(get_db)):
    existing = db.query(Store).filter(Store.name == store.name).first() 
    if existing:
        raise HTTPException(status_code=400, detail="Store with this name already exists")
    return create_store(db=db, store=store)