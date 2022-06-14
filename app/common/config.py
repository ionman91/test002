from functools import lru_cache
from pydantic import BaseSettings


class DBConfig(BaseSettings):
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    EXCEPT_PATH_LIST: list[str] = []
    EXCEPT_PATH_REGEX: str

    EXPIRES_COOKIE_TIME: int

    JWT_SECRET: str
    JWT_ALGORITHM: str

    REDIS_HOST: str
    REDIS_PASSWORD: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    return DBConfig()


settings = get_settings()
