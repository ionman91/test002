from app.database.connect import rd

from datetime import datetime

import re


def now_date():
    return datetime.utcnow()


# chat id 만들기
async def make_chat_id():
    chat_id: str = ''
    while True:
        now = f"{now_date()}"
        split_now = re.split("[-|:|.| ]", now)
        chat_id = ''.join(split_now)
        check_duplicate = await rd.find(chat_id)
        if not check_duplicate:
            break
    return chat_id
