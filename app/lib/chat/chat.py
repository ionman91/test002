from fastapi import WebSocket

from collections import defaultdict


class ChatManager:
    def __init__(self):
        self.connections: dict = defaultdict(dict)
        self.generator = self.get_notification_generator()
        self.my_user = ''

    async def get_notification_generator(self):
        while True:
            message = yield
            msg = message["message"]
            room_name = message["room_name"]
            await self.broadcast(msg, room_name)

    def get_rooms(self):
        return self.connections

    def insert_user(self, user):
        self.insert = user

    def check_duplicate(self, room_name):
        if room_name in self.connections.keys():
            return True
        else:
            return False

    def get_members(self, room_name):
        try:
            return self.connections[room_name]
        except Exception:
            return None

    # def get_member(self, chat_id: int, user: str):
    #     try:
    #         return self.connections[chat_id][user]
    #     except Exception:
    #         return None

    async def push(self, msg: str, room_name: str = None):
        message_body = {"message": msg, "room_name": room_name}
        await self.generator.asend(message_body)

    async def connect(self, websocket: WebSocket, chat_id: int):
        await websocket.accept()
        if len(self.connections[chat_id]) == 0:
            self.connections[chat_id] = []
        self.connections[chat_id].append(websocket)
        print(f"CONNECTIONS : {self.connections[chat_id]}")

    def remove(self, websocket: WebSocket, room_name: str):
        self.connections[room_name].remove(websocket)
        print(f"CONNECTION REMOVED : {self.connections[room_name]}")

    async def broadcast(self, message, chat_id: int):
        # living_connections = []
        # # 안에 존재하는 유저들을 다 빼서 일일이 메세지를 보냄
        # while len(self.connections[room_name]) > 0:
        #     websocket = self.connections[room_name].pop()
        #     await websocket.send_text(message)
        #     # 빼낸 유저들을 다시 living connections 에 집어 넣는다.
        #     living_connections.append(websocket)
        # self.connections[room_name] = living_connections
        for connection in self.connections[chat_id]:
            await connection.send_json(message)


chatManager = ChatManager()


from app.database.connect import rd


class ChatManager22:
    def __init__(self):
        self.connections: list = []
        # self.generator = self.get_notification_generator()
        self.my_user = ''

    # async def get_notification_generator(self):
    #     while True:
    #         message = yield
    #         msg = message["message"]
    #         room_name = message["room_name"]
    #         await self.broadcast(msg, room_name)

    def insert_user(self, user):
        self.insert = user

    def check_duplicate(self, room_name):
        if room_name in self.connections.keys():
            return True
        else:
            return False

    def get_members(self):
        try:
            return self.connections
        except Exception:
            return None

    # def get_member(self, chat_id: int, user: str):
    #     try:
    #         return self.connections[chat_id][user]
    #     except Exception:
    #         return None

    async def push(self, msg: str, room_name: str = None):
        message_body = {"message": msg, "room_name": room_name}
        await self.generator.asend(message_body)

    async def connect22(self, websocket: WebSocket):
        await websocket.accept()

        bbb = await rd.set_value22(websocket)

        if len(self.connections) == 0:
            self.connections = []
        self.connections.append(bbb)
        print(f"CONNECTIONS : {self.connections}")

    def remove(self, websocket: WebSocket):
        self.connections.remove(websocket)
        print(f"CONNECTION REMOVED : {self.connections}")

    async def broadcast(self, message):
        # living_connections = []
        # # 안에 존재하는 유저들을 다 빼서 일일이 메세지를 보냄
        # while len(self.connections[room_name]) > 0:
        #     websocket = self.connections[room_name].pop()
        #     await websocket.send_text(message)
        #     # 빼낸 유저들을 다시 living connections 에 집어 넣는다.
        #     living_connections.append(websocket)
        # self.connections[room_name] = living_connections
        for connection in self.connections:
            await connection.send_json(message)


chat = ChatManager22()
