from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from starlette.responses import JSONResponse

from app.router.models import User
from app.router.schemas import UserRegister, Token, SnsType, UserToken
from app.database.connect import db
from app.common.settings import conf

import jwt
import bcrypt


router = APIRouter()


@router.post("/register/{sns_type}", status_code=201, response_model=Token)
async def register(sns_type: SnsType, user: UserRegister, session: Session = Depends(db.session)):
    if sns_type == SnsType.email:
        is_exist = await is_username_exist(user.username)
        if not sns_type or not user.password:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=dict(msg="모든 정보 다 입력해 짜식아"))
        if is_exist:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=dict(msg="존재하는 유저리야"))
        hash_pw = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
        new_user = User.create(session, auto_commit=True, password=hash_pw, username=user.username, sns_type=sns_type)
        token = dict(Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(new_user).dict(exclude={'password'}),)}")
        return token
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=dict(msg="NOT_SUPPORTED"))


@router.post("/login/{sns_type}", status_code=200, response_model=Token)
async def login(sns_type: SnsType, user: UserRegister):
    print("???")
    if sns_type == SnsType.email:
        is_exist = await is_username_exist(user.username)
        if not user.username or not user.password:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=dict(msg="Email and PW must be provided'"))
        if not is_exist:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=dict(msg="NO_MATCH_USER"))
        exist_user = await is_username_exist(user.username)
        is_verified = bcrypt.checkpw(user.password.encode("utf-8"), exist_user.password.encode("utf-8"))
        if not is_verified:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=dict(msg="NO_MATCH_USER"))
        token = dict(
            Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(exist_user).dict(exclude={'pw'}),)}")
        return token
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=dict(msg="NOT_SUPPORTED"))


async def is_username_exist(username: str):
    get_username = User.get(username=username)
    if get_username:
        return get_username
    return False


def create_access_token(*, data: dict = None, expires_delta: int = int(conf().EXPIRES_COOKIE_TIME)):
    to_encode = data.copy()
    if expires_delta:
        print(datetime.utcnow() + timedelta(hours=expires_delta))
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, conf().JWT_SECRET, algorithm=conf().JWT_ALGORITHM)
    return encoded_jwt
