from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import csv
from io import StringIO

from app.database import get_db
from app.core.security import get_current_active_user
from app.crud.price import create_price, get_prices
from app.crud.discount import get_active_discounts_for_store  # ← NEW
from app.schemas.price import (
    PriceCreate, PriceResponse,
    PriceComparisonResponse, PriceComparisonItem,
    PriceBatchItem, PriceBatchResponse
)
from app.models.user import User
from app.models.price import Price
from app.models.store import Store

router = APIRouter()

# ────── Single price ──────
@router.post("/prices", response_model=PriceResponse)
def add_price(
    price_in: PriceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_approved:
        raise HTTPException(403, detail="Not approved")
    return create_price(db=db, price_in=price_in, user_id=current_user.id)


# ────── List prices ──────
@router.get("/prices", response_model=List[PriceResponse])
def list_prices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_prices(db, skip=skip, limit=limit)


# ────── BATCH UPLOAD (JSON or CSV) ──────
@router.post("/prices/batch", response_model=PriceBatchResponse)
async def batch_upload_prices(
    prices: List[PriceBatchItem] | None = None,
    file: UploadFile | None = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_approved:
        raise HTTPException(403, detail="User not approved")

    if not prices and not file:
        raise HTTPException(400, detail="Send either JSON body or CSV file")

    items: List[PriceBatchItem] = prices or []

    if file:
        if file.content_type not in ["text/csv", "application/vnd.ms-excel", "text/plain"]:
            raise HTTPException(400, detail="File must be CSV")
        content = await file.read()
        csv_data = StringIO(content.decode("utf-8"))
        reader = csv.DictReader(csv_data)
        required = {"product_name", "price", "store_id"}
        for row in reader:
            if not required.issubset(row.keys()):
                raise HTTPException(400, detail=f"CSV missing columns. Need: {required}")
            try:
                items.append(PriceBatchItem(
                    product_name=row["product_name"].strip(),
                    price=float(row["price"]),
                    store_id=int(row["store_id"]),
                    barcode_type=row.get("barcode_type") or None,
                    gtin=row.get("gtin") or None,
                ))
            except (ValueError, KeyError) as e:
                raise HTTPException(400, detail=f"Invalid CSV row: {e}")

    success = 0
    errors = []

    for item in items:
        try:
            create_price(
                db=db,
                price_in=PriceCreate(
                    product_name=item.product_name,
                    price=item.price,
                    store_id=item.store_id,
                    barcode={"barcode_type": item.barcode_type, "gtin": item.gtin} if item.barcode_type or item.gtin else None
                ),
                user_id=current_user.id
            )
            success += 1
        except Exception as e:
            errors.append(f"{item.product_name} @ store {item.store_id}: {str(e)}")

    db.commit()
    return PriceBatchResponse(success_count=success, failed_count=len(errors), errors=errors)


# ────── COMPARE PRICES WITH DISCOUNTS ──────
@router.get("/compare", response_model=PriceComparisonResponse)
def compare_prices(
    product_name: str = Query(..., description="Exact product name (case-insensitive)"),
    lat: float = Query(..., description="Your latitude"),
    lon: float = Query(..., description="Your longitude"),
    radius_km: float = Query(10.0, ge=0.1, le=100),
    db: Session = Depends(get_db)
):
    # Haversine distance
    distance_km = (
        6371 *
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
        raise HTTPException(404, detail=f"No prices found for '{product_name}' nearby")

    items = []
    for price, store, distance in results:
        # Check for active discount
        discount = get_active_discounts_for_store(
            db, store_id=store.id, gtin=price.gtin, product_name=price.product_name
        )

        original_price = price.price
        final_price = original_price
        discount_info: Optional[str] = None

        if discount:
            if discount.discount_percent:
                final_price = round(original_price * (1 - discount.discount_percent / 100), 2)
                discount_info = f"{discount.discount_percent}% off (app only!)"
            elif discount.discount_fixed:
                final_price = round(original_price + discount.discount_fixed, 2)
                discount_info = f"€{abs(discount.discount_fixed):.2f} off (app only!)"

        items.append(PriceComparisonItem(
            store_id=store.id,
            store_name=store.name,
            price=original_price,
            final_price=final_price,           
            discount_info=discount_info,       
            distance_km=round(distance, 2),
            address=store.address,
            lat=store.lat,
            lon=store.lon,
            barcode_type=price.barcode_type,
            gtin=price.gtin,
        ))

    return PriceComparisonResponse(product_name=product_name, results=items)