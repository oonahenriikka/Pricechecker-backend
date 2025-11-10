
from fastapi import FastAPI
from app.database import Base, engine
from app.models import store  


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Price Checker Backend",
    description="TWC 2025 – Team project",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message": "Backend is running! Database ready."}