from fastapi import APIRouter, Request

from app.database.connect import rd
from app import main as m


router = APIRouter()


class Test:
    def __init__(self):
        self._total = 0

    def click(self):
        self._total += 1
        return self._total


test = Test()


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


@router.post("/api/auth/class_test")
async def test_class():
    return {"result": test.click()}
