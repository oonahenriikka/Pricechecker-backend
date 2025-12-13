from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class BarcodeInfo(BaseModel):
    barcode_type: str | None = None
    gtin: str | None = None

class PriceComparisonItem(BaseModel):
    store_id: int
    store_name: str
    price: float
    final_price: float
    discount_info: Optional[str] = None
    distance_km: float
    address: Optional[str] = None
    lat: float
    lon: float
    barcode_type: Optional[str] = None   
    gtin: Optional[str] = None           

    price_label: str

class PriceComparisonResponse(BaseModel):
    product_name: str
    results: list[PriceComparisonItem]

class PriceCreate(BaseModel):
    product_name: str
    price: float
    store_id: int
    barcode: BarcodeInfo | None = None

class PriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    product_name: str
    price: float
    barcode_type: str | None = None
    gtin: str | None = None
    store_id: int
    user_id: int
    created_at: datetime

class PriceBatchItem(BaseModel):
    product_name: str
    price: float
    store_id: int
    barcode_type: str | None = None
    gtin: str | None = None

class PriceBatchResponse(BaseModel):
    success_count: int
    failed_count: int
    errors: list[str] = []
