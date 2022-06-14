from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.lib.chat.chat import chatManager
from app.database.connect import rd


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
                # d = json.loads(data)
                # d["room_name"] = room_name

                # room_members = (
                #     chatManager.get_members(room_name)
                #     if chatManager.get_members(room_name) is not None
                #     else []
                # )
                # if websocket not in room_members:
                #     print("SENDER NOT IN ROOM EMEBERS: RECONNECTING")
                #     await chatManager.connect(websocket, room_name)
                await chatManager.broadcast(data, chat_id)
        except WebSocketDisconnect:
            chatManager.remove(websocket, chat_id)
