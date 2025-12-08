from pydantic import BaseModel, ConfigDict
from typing import Optional

class StoreCreate(BaseModel):
    name: str
    lat: float          
    lon: float         
    address: Optional[str] = None

class StoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    lat: float
    lon: float
    address: Optional[str]