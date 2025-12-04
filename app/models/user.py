
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,        
)
from sqlalchemy.orm import relationship   
from sqlalchemy.sql import func         
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"))
    is_admin = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)      
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    
    store = relationship("Store", back_populates="users")