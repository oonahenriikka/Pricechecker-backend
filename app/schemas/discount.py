from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class DiscountCreate(BaseModel):
    gtin: Optional[str] = None
    product_name: Optional[str] = None
    discount_percent: float = 0.0
    discount_fixed: Optional[float] = None
    valid_until: Optional[datetime] = None

class DiscountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    store_id: int
    gtin: Optional[str]
    product_name: Optional[str]
    discount_percent: float
    discount_fixed: Optional[float]
    valid_until: Optional[datetime]