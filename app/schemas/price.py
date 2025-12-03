from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PriceComparisonItem(BaseModel):
    store_id: int
    store_name: str
    price: float
    distance_km: float
    address: Optional[str] = None
    lat: float
    lon: float

class PriceComparisonResponse(BaseModel):
    product_name: str
    results: list[PriceComparisonItem]

class PriceCreate(BaseModel):
    product_name: str
    price: float
    store_id: int

class PriceResponse(BaseModel):
    id: int
    product_name: str
    price: float
    store_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PriceBatchItem(BaseModel):
    product_name: str
    price: float
    store_id: int

class PriceBatchResponse(BaseModel):
    success_count: int
    failed_count: int
    errors: list[str] = []
