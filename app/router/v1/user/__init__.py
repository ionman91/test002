from fastapi import APIRouter

from app.router.v1.user import api


router = APIRouter()


router.include_router(api.router, prefix="/api/auth")
