from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    
    # ────── BARCODE FIELDS ──────
    barcode_type = Column(String, nullable=True)   # e.g. "EAN13", "UPC", "CODE128"
    gtin = Column(String, unique=False, index=True, nullable=True)  # the actual number

    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())