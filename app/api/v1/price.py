# app/api/v1/price.py
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import csv
from io import StringIO
import math

from app.database import get_db
from app.core.security import get_current_active_user
from app.crud.price import create_price, get_prices
from app.crud.discount import get_active_discounts_for_store
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


# ────── COMPARE PRICES WITH DISCOUNTS + LABELING ──────
@router.get("/compare", response_model=PriceComparisonResponse)
def compare_prices(
    product_name: str = Query(..., description="Exact product name (case-insensitive)", min_length=1),
    lat: float = Query(..., description="Your latitude", ge=-90, le=90),
    lon: float = Query(..., description="Your longitude", ge=-180, le=180),
    radius_km: float = Query(10.0, ge=0.1, le=1000),
    db: Session = Depends(get_db)
):
    results = (
        db.query(Price, Store)
        .join(Store, Price.store_id == Store.id)
        .filter(func.lower(Price.product_name) == product_name.lower())
        .all()
    )

    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371.0
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    filtered = []
    for price, store in results:
        distance = haversine_km(lat, lon, store.lat, store.lon)
        if distance <= radius_km:
            filtered.append((price, store, distance))

    if not filtered:
        raise HTTPException(404, detail=f"No prices found for '{product_name}' nearby")

    final_prices: list[float] = []
    response_items: list[PriceComparisonItem] = []

    for price, store, distance in filtered:
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
            elif discount.discount_fixed is not None:
                final_price = round(max(original_price - discount.discount_fixed, 0), 2)
                discount_info = f"€{abs(discount.discount_fixed):.2f} off (app only!)"

        final_prices.append(final_price)

        response_items.append({
            "store": store,
            "original_price": original_price,
            "final_price": final_price,
            "discount_info": discount_info,
            "distance": distance,
            "price_obj": price,
        })

    avg_price = sum(final_prices) / len(final_prices) if final_prices else 0

    labeled_items: list[PriceComparisonItem] = []
    for item in response_items:
        ratio = item["final_price"] / avg_price if avg_price > 0 else 1.0
        if ratio <= 0.75:
            label = "very inexpensive"
        elif ratio <= 0.9:
            label = "inexpensive"
        elif ratio <= 1.1:
            label = "average"
        elif ratio <= 1.3:
            label = "expensive"
        else:
            label = "very expensive"

        labeled_items.append(PriceComparisonItem(
            store_id=item["store"].id,
            store_name=item["store"].name,
            price=item["original_price"],
            final_price=item["final_price"],
            discount_info=item["discount_info"],
            price_label=label,
            distance_km=round(item["distance"], 2),
            address=item["store"].address,
            lat=item["store"].lat,
            lon=item["store"].lon,
            barcode_type=item["price_obj"].barcode_type,
            gtin=item["price_obj"].gtin,
        ))

    return PriceComparisonResponse(product_name=product_name, results=labeled_items)