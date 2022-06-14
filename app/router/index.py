from fastapi import APIRouter, Request

from app.database.connect import rd
from app import main as m
from app.lib.chat.chat import chatManager


router = APIRouter()


@router.get("/")
async def main(request: Request):
    print('asdfasd')
    print(chatManager.get_members('20220613170344987084'))
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
    user_info = request.state.user
    await rd.add_participant(chat_id, user_info['username'], user_info)

    return m.templates.TemplateResponse(
        'chat/detail.html', {"request": request}
    )


@router.get("/chat/detail/{room_name}/{user_name}")
async def chat_detail(room_name: str, user_name: str, request: Request):
    return m.templates.TemplateResponse(
        "chat/detail.html", {"request": request})
