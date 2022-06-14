# from fastapi import APIRouter, Depends, status, Request

# from sqlalchemy.orm import Session

# from app.router.models import ChatBoard, User
# from app.router.schemas import ChatBoardBase, ChatBoardList

# from app.database.connect import db

from fastapi import APIRouter, Request, status

from datetime import datetime

from app.database.connect import rd
from app.router.schemas import ChatBoardBase, ChatInfoId
from app.router.v1.chat.chat import make_chat_id

import json


router = APIRouter()


"""
    coding - 채팅방을 redis 에 저장하게 되었을 경우
"""


@router.get("/get_rooms", status_code=status.HTTP_200_OK)
async def get_rooms():
    rooms = await rd.get_all()
    return rooms


"""
    coding - 채팅방을 서버에 저장하게 되었을 경우
"""


@router.post("/add_room", status_code=status.HTTP_201_CREATED)
async def add_room(chat: ChatBoardBase, request: Request):
    chat_id = await make_chat_id()
    username = request.state.user['username']
    chat_info = {
        'title': chat.title,
        'created_at': f"{datetime.utcnow()}",
        'participants': {},
        'made_by': request.state.user
    }
    chat_info['participants'][username] = request.state.user
    chat_info = json.dumps(chat_info, ensure_ascii=False)

    await rd.set_value(chat_id, chat_info)

    return {"chat_id": chat_id}


"""
    coding - 유저를 추가
"""


@router.get("/add_user/{chat_id}")
async def add_user(chat_id: int, request: Request):
    user_info = request.state.user
    await rd.add_participant(chat_id, user_info['username'], user_info)
    return True


"""
    coding - 채팅방의 정보를 보냄
"""


@router.get("/get_chat_info/{chat_id}")
async def get_chat_info(chat_id: int):
    return await rd.get_value(chat_id)



# @router.get("/get_rooms", response_model=list[ChatBoardList])
# async def get_rooms(session: Session = Depends(db.session)):
#     rooms = session.query(ChatBoard).all()

#     return rooms


# @router.post("/add_room", status_code=status.HTTP_201_CREATED, response_model=ChatBoardList)
# async def add_room(chat_info: ChatBoardBase, request: Request, session: Session = Depends(db.session)):
#     """
#         request.state.user 에 유저의 정보가 담겨있다.
#     """
#     chat_room = ChatBoard(title=chat_info.title)
#     session.add(chat_room)
#     session.commit()

#     made_by_user = session.query(User).filter(User.id == request.state.user['id']).first()
#     made_by_user.chat_room_id = chat_room.id
#     session.add(made_by_user)
#     session.commit()

#     return chat_room
