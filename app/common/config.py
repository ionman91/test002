from functools import lru_cache
from pydantic import BaseSettings


class DBConfig(BaseSettings):
    DB_URL: str

    EXCEPT_PATH_LIST: list[str] = []
    EXCEPT_PATH_REGEX: str

    EXPIRES_COOKIE_TIME: int

    JWT_SECRET: str
    JWT_ALGORITHM: str

    REDIS_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    return DBConfig()


settings = get_settings()
