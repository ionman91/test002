from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.lib.chat.chat import chatManager

import logging


router = APIRouter()


@router.websocket("/ws/{chat_id}/{sender}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, sender: str):
    # sender = websocket.cookies.get("X-Authorization")
    if sender:
        await chatManager.connect(websocket, chat_id)
        # await rd.make_user_websocket(chat_id, sender, websocket)
        welcome_msg = {
            "status": "first",
            "sender": sender,
        }
        await chatManager.broadcast(welcome_msg, chat_id)
        try:
            while True:
                data = await websocket.receive_json()
                logging.info(f"현재 접속된 유저들은 === {chatManager.get_members(chat_id)}")
                # d = json.loads(data)
                # d["room_name"] = room_name

                # room_members = (
                #     chatManager.get_members(chat_id)
                #     if chatManager.get_members(chat_id) is not None
                #     else []
                # )
                # if websocket not in room_members:
                #     print("SENDER NOT IN ROOM EMEBERS: RECONNECTING")
                #     await chatManager.connect(websocket, room_name)
                await chatManager.broadcast(data, chat_id)
        except WebSocketDisconnect:
            chatManager.remove(websocket, chat_id)
            welcome_msg = {
                "status": "last",
                "sender": sender,
            }
            await chatManager.broadcast(welcome_msg, chat_id)
