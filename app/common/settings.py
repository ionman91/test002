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


@dataclass
class LocalConfig(Config):
    REDIS_URL: str = "redis://localhost"
    REDIS_PWD: str = "1234"

    DB_URL: str = "mysql+pymysql://admin:1234@localhost:3306/dev?charset=utf8mb4"

    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]


@dataclass
class ProdConfig(Config):
    REDIS_URL: str = f"redis://{settings.REDIS_HOST}"
    REDIS_PWD: str = settings.REDIS_PASSWORD

    DB_URL: str = f"mysql+pymysql://admin:qweasdzx@test-rds.ctnwpgtfxzsl.ap-northeast-2.rds.amazonaws.com:3306/test?charset=utf8mb4"

    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]


def conf():
    config = dict(prod=ProdConfig(), local=LocalConfig())
    return config.get(environ.get("API_ENV", "prod"))
