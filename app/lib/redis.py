from fastapi import FastAPI

# from redis import Redis

import logging
import aioredis
import json


logging.basicConfig(level=logging.INFO)


class Redis:
    def __init__(self, app: FastAPI = None, **kwargs):
        self._redis = None
        if app is not None:
            self.init_redis(**kwargs)

    def init_redis(self, **kwargs):
        env = kwargs.get('API_ENV')
        url = kwargs.get("REDIS_URL")
        if env == 'local':
            self._redis = aioredis.from_url(url)
        elif env == 'prod':
            self._redis = aioredis.from_url(
                url, encoding="utf-8", decode_responses=True
            )

    def get_rd(self):
        # redis 접속을 내보낸다.
        return self._redis

    async def set_value(self, key, value):
        # redis 에 key, value 를 넣는다.
        await self._redis.set(key, value)
        await self._redis.close()

    async def get_value(self, key):
        # redis key 로 value 를 불러온다.
        value = await self._redis.get(key)
        await self._redis.close()

        if value:
            value = json.loads(value)
        return value

    async def delete_key(self, key):
        await self._redis.delete(key)
        await self._redis.close()

    async def get_all(self) -> dict:
        # redis 에 저장되어 있는 모든 값들을 가지고 온다.
        _datas: dict = {}
        keys = await self._redis.keys()
        if keys:
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


rd = Redis()
