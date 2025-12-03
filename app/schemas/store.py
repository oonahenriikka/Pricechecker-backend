# app/schemas/store.py
from pydantic import BaseModel
from typing import Optional

class StoreCreate(BaseModel):
    name: str
    lat: float          
    lon: float         
    address: Optional[str] = None

class StoreResponse(BaseModel):
    id: int
    name: str
    lat: float
    lon: float
    address: Optional[str]

    class Config:
        from_attributes = True