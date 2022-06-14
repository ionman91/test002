from fastapi import APIRouter, Request

from app.database.connect import rd
from app import main as m


router = APIRouter()


@router.get("/")
async def main(request: Request):
    return m.templates.TemplateResponse(
        'user/base.html', {"request": request}
    )


@router.get("/chat/list")
async def chat(request: Request):
    return m.templates.TemplateResponse(
        'chat/list.html', {"request": request}
    )


@router.get("/chat/detail/{chat_id}")
async def chat_detail(chat_id: int, request: Request):
    return m.templates.TemplateResponse(
        'chat/detail.html', {"request": request}
    )
