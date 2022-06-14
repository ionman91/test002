from pydantic import BaseModel
from enum import Enum


"""

    user table 관련 schema

"""


class SnsType(str, Enum):
    email: str = "email"
    facebook: str = "facebook"
    google: str = "google"
    kakao: str = "kakao"


class UserBase(BaseModel):
    username: str


class UserRegister(UserBase):
    password: str


class Token(BaseModel):
    Authorization: str = None


class UserToken(UserBase):
    id: int
    sns_type: str

    class Config:
        orm_mode = True


class UserInfo(UserBase):
    id: int

    class Config:
        orm_mode = True


"""

    chat table 관련 schema

"""


class ChatBoardBase(BaseModel):
    title: str


class ChatInfoId(BaseModel):
    chat_id: int

# class ChatBoardList(ChatBoardBase):
#     id: int
#     participants: list[UserInfo] = []

#     class Config:
#         orm_mode = True


"""

    일반 bool 관련 schema

"""


class BoolStatus(BaseModel):
    is_bool: bool
