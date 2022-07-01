from fastapi import APIRouter

from app.router.v1.chat import api


router = APIRouter()


router.include_router(api.router)
