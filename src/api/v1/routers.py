# src/api/v1/routers.py
from fastapi import APIRouter
from src.api.v1.endpoints import users, clients, products, sales, transactions, wages, allergies, allergies_history, labs, anthropometrics, next_of_kin, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(anthropometrics.router, prefix="/client/anthropometrics", tags=["anthropometrics"])
api_router.include_router(allergies.router, prefix="/client/allergies", tags=["allergies"])
api_router.include_router(allergies_history.router, prefix="/client/allergies/history", tags=["allergies-history"])
api_router.include_router(next_of_kin.router, prefix="/client/nextofkin", tags=["next-of-kin"])
api_router.include_router(products.router, prefix="/products", tags=["products"])