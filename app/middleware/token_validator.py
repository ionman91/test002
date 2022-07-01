from jwt.exceptions import ExpiredSignatureError, DecodeError
from starlette.requests import Request
from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.common.settings import conf
from app.errors import exceptions as ex

from app.utils.date_utils import D

import time
import typing
import re
import jwt


class AccessControl:
    def __init__(
        self,
        app: ASGIApp,
        except_path_list: typing.Sequence[str] = None,
        except_path_regex: str = None,
    ) -> None:
        if except_path_list is None:
            except_path_list = ["*"]
        self.app = app
        self.except_path_list = except_path_list
        self.except_path_regex = except_path_regex

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (scope['type'] == 'websocket'):
            token = str(scope['query_string'])
            access_token = re.split("(?:b'token=)|\'", str(token))[1].replace('%20', ' ')
            is_validator = await self.token_decode(access_token=str(access_token))
            if is_validator:
                pass
        else:
            request = Request(scope=scope)
            headers = Headers(scope=scope)
            request.state.start = time.time()
            request.state.inspect = None
            request.state.user = None
            request.state.is_admin_access = None
            # ip_from = request.headers["x-forwarded-for"] if "x-forwarded-for" in request.headers.keys() else None

            if await self.url_pattern_check(request.url.path, self.except_path_regex) or request.url.path in self.except_path_list:
                return await self.app(scope, receive, send)

            if request.url.path.startswith("/api"):
                # api 인경우 헤더로 토큰 검사
                if "authorization" in request.headers.keys():
                    request.state.user = await self.token_decode(access_token=request.headers.get("authorization"))
                    # 토큰 없음
                else:
                    if "authorization" not in request.headers.keys():
                        response = JSONResponse(status_code=401, content=dict(msg="AUTHORIZATION_REQUIRED"))
                        return await response(scope, receive, send)
            else:
                # 템플릿 렌더링인 경우 쿠키에서 토큰 검사
                # request.cookies["Authorization"] = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MTQsImVtYWlsIjoia29hbGFAZGluZ3JyLmNvbSIsIm5hbWUiOm51bGwsInBob25lX251bWJlciI6bnVsbCwicHJvZmlsZV9pbWciOm51bGwsInNuc190eXBlIjpudWxsfQ.4vgrFvxgH8odoXMvV70BBqyqXOFa2NDQtzYkGywhV48"
                if "Authorization" not in request.cookies.keys():
                    response = JSONResponse(status_code=401, content=dict(msg="AUTHORIZATION_REQUIRED"))
                    return await response(scope, receive, send)

                request.state.user = await self.token_decode(access_token=request.cookies.get("Authorization"))

            request.state.req_time = D.datetime()
            # print('datetime(): ', D.datetime())
            # print('date: ', D.date())
            # print('date_num: ', D.date_num())

            # print('request,cookies: ', request.cookies)
            # print('headers: ', headers)
        res = await self.app(scope, receive, send)
        return res

    @staticmethod
    async def url_pattern_check(path, pattern):
        result = re.match(pattern, path)
        if result:
            return True
        return False

    @staticmethod
    async def token_decode(access_token):
        """
        :param access_token:
        :return:
        """
        try:
            access_token = access_token.replace("Bearer ", "")
            payload = jwt.decode(access_token, key=conf().JWT_SECRET, algorithms=[conf().JWT_ALGORITHM])
        except ExpiredSignatureError:
            raise ex.TokenExpiredEx()
        except DecodeError:
            raise ex.TokenDecodeEx()
        return payload
