from fastapi import APIRouter
from api.endpoints import auth, users, logout, otp

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(logout.router, prefix="/auth", tags=["auth"])
api_router.include_router(otp.router, prefix="/auth", tags=["auth"])