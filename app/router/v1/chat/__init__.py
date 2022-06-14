from fastapi import APIRouter

from app.router.v1.chat import api, websocket


router = APIRouter()


router.include_router(api.router, prefix="/api/chat")
router.include_router(websocket.router)
