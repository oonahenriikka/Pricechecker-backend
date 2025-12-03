# app/models/store.py
from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    lat = Column(Float, nullable=False)   
    lon = Column(Float, nullable=False)   
    address = Column(String, nullable=True)