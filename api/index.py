# main.py
from fastapi import FastAPI
from src.api.v1.routers import api_router
from src.database.db import Base, engine

app = FastAPI(title="PS Manager", version="1.0.0")

# Create database tables (if applicable, may need reflection for existing DB)
Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to PS Manager"}