from pydantic import BaseModel
from datetime import datetime

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