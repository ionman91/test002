from fastapi import FastAPI

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import logging
import aioredis
import json


class Redis:
    def __init__(self, app: FastAPI = None, **kwargs):
        self._redis = None
        if app is not None:
            self.init_redis(**kwargs)

    def init_redis(self, **kwargs):
        url = kwargs.get("REDIS_URL")
        pwd = kwargs.get("REDIS_PWD")

        self._redis = aioredis.from_url(url, password=pwd)

    async def set_value(self, key, value):
        await self._redis.set(key, value)
        await self._redis.close()

    async def set_values(self, *args):
        for key, value in args[0].items():
            await self._redis.set(key, value)
        await self._redis.close()

    async def get_value(self, key):
        value = await self._redis.get(key)
        await self._redis.close()

        return json.loads(value)

    async def get_all(self) -> dict:
        _datas: dict = {}
        keys = await self._redis.keys()

        for key in keys:
            decoded_key = json.loads(key)
            value = await self._redis.get(key)
            _datas[decoded_key] = json.loads(value)

        await self._redis.close()
        return _datas

    async def find(self, key):
        value = await self._redis.exists(key)
        await self._redis.close()

        return True if value == 1 else False

    async def add_participant(self, chat_id, username, user_info):
        chat_info = await self.get_value(chat_id)
        if username in chat_info['participants'].keys():
            return False

        chat_info['participants'][username] = user_info
        chat_info = json.dumps(chat_info, ensure_ascii=False)
        await self.set_value(chat_id, chat_info)

    async def is_check_user(self, chat_id, username):
        chat_info = await self.get_value(chat_id)
        if username in chat_info['participants'].keys():
            return True
        return False

    # async def make_user_websocket(self, chat_id, user, websocket):
    #     chat_info = await self.get_value(chat_id)
    #     chat_info['participants'][user]['websocket'] = websocket
    #     chat_info = json.dumps(chat_info, ensure_ascii=False)
    #     await self.set_value(chat_id, chat_info)


class SQLAlchemy:
    def __init__(self, app: FastAPI = None, **kwargs):
        self._engine = None
        self._session = None
        if app is not None:
            self.init_app(app=app, **kwargs)

    def init_app(self, app: FastAPI, **kwargs):
        """
        echo, pool_recycle, pool_pre_ping=True 확인해보자
        """
        database_url = kwargs.get("DB_URL")

        self._engine = create_engine(database_url)

        self._session = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
        )

        @app.on_event("startup")
        def startup():
            self._engine.connect()
            logging.info("DB connected.")

        @app.on_event("shutdown")
        def shutdown():
            self._session.close_all()
            self._engine.dispose()
            logging.info("DB disconnected.")

    def get_db(self):
        if self._session is None:
            raise Exception("must be called 'init_app'")
        db_session = None
        try:
            db_session = self._session()
            yield db_session
        finally:
            db_session.close()

    @property
    def session(self):
        return self.get_db

    @property
    def engine(self):
        return self._engine


rd = Redis()
db = SQLAlchemy()

Base = declarative_base()