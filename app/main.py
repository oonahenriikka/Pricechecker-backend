# app/main.py
from fastapi import FastAPI
from app.api.v1 import auth, store, price, discount, admin  
from app.database import Base, engine

# ────── FastAPI app instance ──────
app = FastAPI(
    title="Price Checker Backend",
    description="PSA 2025 – Full barcode + app-only discounts + batch upload",
    version="1.0.0",
)

# ────── Create all tables (Price, Store, User, Discount, etc.) ──────
Base.metadata.create_all(bind=engine)

# ────── Include all routers ──────
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(store.router, prefix="/api/v1", tags=["stores"])
app.include_router(price.router, prefix="/api/v1", tags=["prices"])
app.include_router(discount.router, prefix="/api/v1", tags=["discounts"])   # ← NOW WORKS
app.include_router(admin.router, prefix="/api/v1")

# ────── Root endpoint ──────
@app.get("/")
def root():
    return {"message": "Price Checker API v1 is running — discounts & barcodes ready!"}