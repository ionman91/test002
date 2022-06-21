from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from aioredis.client import Redis, PubSub

import aioredis
import asyncio
import async_timeout
import json
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()


STOPWORD = "STOP"

"""
{'type':'message', 'pattern':None, 'channel':b'channel:1', 'data':b'hello'}
"""


@router.websocket("/ws/{chat_id}")
async def main(websocket: WebSocket, chat_id: str):
    await websocket.accept()

    # redis = await aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)

    redis = aioredis.from_url(
        "redis://jjoontopia-redis.5m2cdo.ng.0001.apn2.cache.amazonaws.com:6379",
        encoding="utf-8", decode_responses=True
    )

    pubsub = redis.pubsub()

    consumer_task = publisher(redis, websocket, chat_id)
    producer_task = sender(pubsub, websocket, chat_id)
    done, pending = await asyncio.wait(
        [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED,
    )
    logger.debug(f"Done task: {done}")


async def publisher(redis: Redis, websocket: WebSocket, chat_id: str):
    pubsub = redis.pubsub()
    while True:
        try:
            message = await websocket.receive_json()
            logging.info(f"message 의 type 은 ==== {type(message)}")
            msg = json.dumps(message)
            if message:
                await redis.publish(chat_id, msg)
        except WebSocketDisconnect:
            pubsub.unsubscribe(chat_id)



async def sender(channel: PubSub, websocket: WebSocket, chat_id: str):
    await channel.subscribe(chat_id)

    while True:
        try:
            # async with async_timeout.timeout(1):
            message = await channel.get_message(ignore_subscribe_messages=True)

            if message is not None:
                logging.info(f"message===={message}")
                logging.info(f"message===={message['data']}")
                msg = json.loads(message['data'])
                await websocket.send_json({
                    'status': '',
                    'sender': msg['sender'],
                    'message': msg['message']
                })
            # await asyncio.sleep(0.01)
        except WebSocketDisconnect:
            channel.unsubscribe(chat_id)
