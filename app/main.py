# app/main.py
from fastapi import FastAPI
from app.api.v1 import auth, store, price
from app.database import Base, engine

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Price Checker Backend",
    description="TWC 2025 – Team project",
    version="1.0.0",
)

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(store.router, prefix="/api/v1", tags=["stores"])
app.include_router(price.router, prefix="/api/v1", tags=["prices"])

@app.get("/")
def root():
    return {"message": "Price Checker API v1 is running!"}