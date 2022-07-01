from fastapi import APIRouter, Depends, status, Request, WebSocket, WebSocketDisconnect

from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from aioredis.client import Redis, PubSub

from app.router.models import ChatBoard, User
from app.router.schemas import ChatBoardBase, ChatBoardList
from app.database.connect import db
from app.lib.redis import rd
from app.router.v1.chat.func import addMember, deleteMember, readMember

import asyncio
import json
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()


"""
    api router

    request.state.user 에 유저의 정보가 담겨있다.
"""


# /chat/list - 채팅 목록을 전부 검색한다.
@router.get("/api/chat/get_rooms", response_model=list[ChatBoardList])
async def get_rooms(session: Session = Depends(db.session)):
    rooms = session.query(ChatBoard).all()

    return rooms


# /chat/list - 채팅방을 만듬
@router.post("/api/chat/add_room", status_code=status.HTTP_201_CREATED, response_model=ChatBoardList)
async def add_room(chat_info: ChatBoardBase, request: Request, session: Session = Depends(db.session)):
    user = session.query(User).filter(User.id == request.state.user['id']).first()
    if user:
        participants = json.dumps([])
        chat_room = ChatBoard(title=chat_info.title, made_by=user.id, participants=participants)
        session.add(chat_room)
        session.commit()

        return chat_room
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=dict(msg="존재하지 않는 유저입니다"))


# /chat/detail - 채팅방의 정보를 얻는다
@router.get("/api/chat/get_chat_info/{chat_id}", response_model=ChatBoardList)
async def add_user(chat_id: int, session: Session = Depends(db.session)):
    chat_room = session.query(ChatBoard).filter(ChatBoard.id == chat_id).first()

    if chat_room:
        return chat_room
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=dict(msg="존재하지 않는 채팅방입니다."))


# /chat/detail - 멤버를 삭제한다.
@router.post("/api/chat/delete_member/{chat_id}")
async def delete_member(chat_id: int, request: Request, session: Session = Depends(db.session)):
    await deleteMember(chat_id, request.state.user['username'], session)
    return {"result": "success"}


# /chat/detail - redis 에 cache 되어 있는 해당 채팅방의 멤버들을 불러온다.
@router.get("/api/chat/get_participants/{chat_id}")
async def get_participants(chat_id: int):
    participants = await readMember(chat_id)
    return {'participants': participants}


"""
    websocket

    sender message event 구성
    {
        'type':'message',
        'pattern':None,
        'channel':b'[channel name]',
        'data':b'{status: "", sender: "", message: ""}'
    }
"""


@router.websocket("/ws/{chat_id}/{current_user}")
async def main(websocket: WebSocket, current_user: str, chat_id: str, session: Session = Depends(db.session)):
    # 처음 websocket 이 열리게 되었을 때 멤버를 추가 해준다.
    await websocket.accept()
    await addMember(chat_id, current_user, session)

    redis = rd.get_rd()
    pubsub = redis.pubsub()

    consumer_task = publisher(redis, pubsub, websocket, current_user, chat_id)
    producer_task = sender(pubsub, websocket, current_user, chat_id)
    done, pending = await asyncio.wait(
        [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED,
    )
    logging.info(f"Done task: {done}")
    # logger.debug(f"Done task: {done}")
    for task in pending:
        logging.info(f"Canceling task: {task}")
        # logger.debug(f"Canceling task: {task}")
        task.cancel()


async def publisher(redis: Redis, channel: PubSub, websocket: WebSocket, current_user: str, chat_id: str):
    while True:
        try:
            message = await websocket.receive_json()
            msg = json.dumps(message)
            if message:
                await redis.publish(chat_id, msg)
        except WebSocketDisconnect:
            await deleteMember(chat_id, current_user)
            msg = {
                    'status': 'exit_user',
                    'sender': current_user,
                    'message': ''
                }
            await redis.publish(chat_id, json.dumps(msg))
            await channel.unsubscribe(chat_id)
            break


async def sender(channel: PubSub, websocket: WebSocket, current_user: str, chat_id: str):
    await channel.subscribe(chat_id)

    while True:
        try:
            message = await channel.get_message(ignore_subscribe_messages=True)

            if message is not None:
                msg = json.loads(message['data'])

                await websocket.send_json({
                    'status': msg['status'],
                    'sender': msg['sender'],
                    'message': msg['message']
                })
        except WebSocketDisconnect:
            await deleteMember(chat_id, current_user)
            await channel.unsubscribe(chat_id)
            break
