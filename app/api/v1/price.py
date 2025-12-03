from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.core.security import get_current_active_user
from app.crud.price import create_price, get_prices
from app.schemas.price import PriceCreate, PriceResponse, PriceComparisonResponse, PriceComparisonItem
from app.models.user import User
from app.models.price import Price
from app.models.store import Store

router = APIRouter()

# ────── Add single price ──────
@router.post("/prices", response_model=PriceResponse)
def add_price(
    price_in: PriceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_approved:
        raise HTTPException(403, detail="Not approved")
    return create_price(db=db, price_in=price_in, user_id=current_user.id)


# ────── List all prices (admin or debug) ──────
@router.get("/prices", response_model=List[PriceResponse])
def list_prices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_prices(db, skip=skip, limit=limit)


# ────── COMPARE PRICES NEAR ME (the killer feature!) ──────
@router.get("/compare", response_model=PriceComparisonResponse)
def compare_prices(
    product_name: str = Query(..., description="Exact product name (case-insensitive)"),
    lat: float = Query(..., description="Your latitude"),
    lon: float = Query(..., description="Your longitude"),
    radius_km: float = Query(10.0, ge=0.1, le=100, description="Search radius in km"),
    db: Session = Depends(get_db)
):
    # Haversine formula – calculates real distance on Earth
    distance_km = (
        6371 *  # Earth's radius in km
        func.acos(
            func.cos(func.radians(lat)) *
            func.cos(func.radians(Store.lat)) *
            func.cos(func.radians(Store.lon) - func.radians(lon)) +
            func.sin(func.radians(lat)) *
            func.sin(func.radians(Store.lat))
        )
    )

    results = (
        db.query(Price, Store, distance_km.label("distance"))
        .join(Store, Price.store_id == Store.id)
        .filter(func.lower(Price.product_name) == product_name.lower())
        .filter(distance_km <= radius_km)
        .order_by(Price.price.asc(), distance_km)
        .all()
    )

    if not results:
        raise HTTPException(404, detail=f"No prices found for '{product_name}' within {radius_km} km")

    items = [
        PriceComparisonItem(
            store_id=store.id,
            store_name=store.name,
            price=price.price,
            distance_km=round(distance, 2),
            address=store.address,
            lat=store.lat,
            lon=store.lon,
        )
        for price, store, distance in results
    ]

    return PriceComparisonResponse(product_name=product_name, results=items)