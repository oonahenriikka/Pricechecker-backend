from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Discount(Base):
    __tablename__ = "discounts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Which store offers the discount
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    
    # Optional: match by GTIN (recommended) or product_name
    gtin = Column(String, nullable=True, index=True)
    product_name = Column(String, nullable=True, index=True)  # fallback
    
    # Discount value
    discount_percent = Column(Float, nullable=False)  # e.g. 15.0 = 15%
    discount_fixed = Column(Float, nullable=True)     # e.g. -0.50 € (optional)

    # Optional: validity period
    valid_from = Column(DateTime(timezone=True), default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=True)

    # Who created it
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())