from dataclasses import dataclass
from dotenv import load_dotenv
from os import path, environ, getenv


load_dotenv()

base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


@dataclass
class Config:
    """
    아래 세팅 값은 뭔지 한번 알아보자
    DB_POOL_RECYCLE:int = 900
    DB_ECHO:bool = True
    """
    BASE_DIR: str = base_dir


@dataclass
class LocalConfig(Config):
    API_ENV: str = 'local'

    DB_URL: str = getenv('DB_URL')
    REDIS_URL: str = getenv('REDIS_URL')
    RMQ_URL: str = getenv('RMQ_URL')

    EXCEPT_PATH_LIST = getenv('EXCEPT_PATH_LIST')
    EXCEPT_PATH_REGEX: str = getenv('EXCEPT_PATH_REGEX')
    EXPIRES_COOKIE_TIME: int = getenv('EXPIRES_COOKIE_TIME')

    JWT_SECRET: str = getenv('JWT_SECRET')
    JWT_ALGORITHM: str = getenv('JWT_ALGORITHM')

    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]


@dataclass
class ProdConfig(Config):
    API_ENV: str = 'prod'

    DB_URL: str = environ.get('DB_URL')
    REDIS_HOST: str = environ.get('REDIS_HOST')
    REDIS_PORT: str = environ.get('REDIS_PORT')
    REDIS_USER: str = environ.get('REDIS_USER')
    RMQ_URL: str = environ.get('RMQ_URL')

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
    return config.get(environ.get("API_ENV", "local"))
