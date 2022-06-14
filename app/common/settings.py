from dataclasses import dataclass
from os import path, environ

from app.common.config import settings


base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


@dataclass
class Config:
    """
    아래 세팅 값은 뭔지 한번 알아보자
    DB_POOL_RECYCLE:int = 900
    DB_ECHO:bool = True
    """
    BASE_DIR: str = base_dir

    DB_URL: str = settings.DB_URL
    REDIS_URL: str = settings.REDIS_URL
    REDIS_PWD: str = settings.REDIS_PWD

    EXCEPT_PATH_LIST = settings.EXCEPT_PATH_LIST
    EXCEPT_PATH_REGEX: str = settings.EXCEPT_PATH_REGEX
    EXPIRES_COOKIE_TIME: int = settings.EXPIRES_COOKIE_TIME

    JWT_SECRET: str = settings.JWT_SECRET
    JWT_ALGORITHM: str = settings.JWT_ALGORITHM


@dataclass
class LocalConfig(Config):
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]


@dataclass
class ProdConfig(Config):
    DB_URL: str = environ.get('DB_URL')
    REDIS_URL: str = environ.get('REDIS_URL')
    REDIS_PWD: str = environ.get('REDIS_PWD', "")

    EXCEPT_PATH_LIST = environ.get('EXCEPT_PATH_LIST')
    EXCEPT_PATH_REGEX: str = environ.get('EXCEPT_PATH_REGEX')
    EXPIRES_COOKIE_TIME: int = environ.get('EXPIRES_COOKIE_TIME')

    JWT_SECRET: str = environ.get('JWT_SECRET')
    JWT_ALGORITHM: str = environ.get('JWT_ALGORITHM')
    DB_URL: str = environ.get('DB_URL')

    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]


def conf():
    config = dict(prod=ProdConfig(), local=LocalConfig())
    return config.get(environ.get("API_ENV", "prod"))
