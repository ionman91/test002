from fastapi import APIRouter
from app.router import v1, index


router = APIRouter()


router.include_router(index.router)
router.include_router(v1.router)
