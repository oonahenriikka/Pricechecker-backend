from pydantic import BaseModel, Field

class StoreBase(BaseModel):
    name: str = Field(..., example="K-Market Kamppi")
    latitude: float = Field(..., example=60.1699)
    longitude: float = Field(..., example=24.9332)

class StoreCreate(StoreBase):
    pass

class StoreResponse(StoreBase):
    id: int

    class Config:
        from_attributes = True  