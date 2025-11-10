from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
  
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    
    store = relationship("Store", back_populates="users")