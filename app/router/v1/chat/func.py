from app.lib.redis import rd
from app.database.connect import db
from app.router.models import ChatBoard
from sqlalchemy.orm import Session

import json


CHAT_LIMIT_MEMBERS = 4  # 추후 채팅방마다 방장이 원하는 대로 인원 수를 넣어보자
CHAT_REDIS_NAME = 'chat_members_in_'  # redis 에 저장할 chat members name


"""
    function
"""


# function - redis 안에 cache 한다.
async def add_member_in_redis(chat_id: int, current_user: str):
    participants = await rd.get_value(f"{CHAT_REDIS_NAME}{chat_id}")
    if not participants:
        participants = [current_user]
    else:
        participants.append(current_user)

    await rd.set_value(
        f"{CHAT_REDIS_NAME}{chat_id}",
        json.dumps(participants).encode('utf-8')
    )


# function - redis 안에 member 를 없앤다.
async def remove_member_in_redis(chat_id: int, current_user: str):
    participants = await rd.get_value(f"{CHAT_REDIS_NAME}{chat_id}")
    if participants:
        participants.remove(current_user)
        if len(participants) == 0:
            await rd.delete_key(f"{CHAT_REDIS_NAME}{chat_id}")
        else:
            await rd.set_value(
                f"{CHAT_REDIS_NAME}{chat_id}",
                json.dumps(participants).encode('utf-8')
            )


# function - 멤버를 채팅방에 추가 한다
# 이 때 redis 로 만들어 참가자를 cache 해놔야 한다.
async def addMember(chat_id: int, current_user: str, session: Session):
    # session = next(db.session())
    chat_room = session.query(ChatBoard).filter(ChatBoard.id == chat_id).first()
    if chat_room:
        participants = json.loads(chat_room.participants)
        # 채팅방에 인원이 다 차게 되면 error 를 내 보낸다. (나중 구현)
        if len(participants) >= CHAT_LIMIT_MEMBERS:
            return False
        else:
            await add_member_in_redis(chat_id, current_user)

            participants.append(current_user)
            chat_room.participants = json.dumps(participants).encode('utf-8')

            session.add(chat_room)
            session.commit()


# function - 멤버를 채팅방에서 삭제 한다.
# 이 때 redis 에서 참가자도 같이 제거 한다.
async def deleteMember(chat_id: int, current_user: str, session: Session = None):
    if not session:
        session = next(db.session())
    chat_room = session.query(ChatBoard).filter(ChatBoard.id == chat_id).first()
    if chat_room:
        await remove_member_in_redis(chat_id, current_user)
        participants = json.loads(chat_room.participants)
        participants.remove(current_user)
        if len(participants) == 0:
            session.delete(chat_room)
        else:
            chat_room.participants = json.dumps(participants).encode('utf-8')
            session.add(chat_room)
        session.commit()


# function - 멤버를 redis 에서 읽어온다.
async def readMember(chat_id: int):
    return await rd.get_value(f"{CHAT_REDIS_NAME}{chat_id}")
