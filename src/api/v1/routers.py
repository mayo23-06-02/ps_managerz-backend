# src/api/v1/routers.py
from fastapi import APIRouter
from src.api.v1.endpoints import users, clients, products, sales, transactions, wages, allergies, labs, anthropometrics, allergies_history

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(anthropometrics.router, prefix="/client/anthropometrics", tags=["anthropometrics"])
api_router.include_router(allergies.router, prefix="/client/allergies", tags=["allergies"])
api_router.include_router(allergies_history.router, prefix="/client/allergies/history", tags=["allergies-history"])