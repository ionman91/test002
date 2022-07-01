from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from dataclasses import asdict
from starlette.middleware.cors import CORSMiddleware

from app.database.connect import db
from app.lib.redis import rd
from app.common.settings import conf
from app.middleware.token_validator import AccessControl
from app.middleware.trusted_hosts import TrustedHostMiddleware
from app.router import router


app = FastAPI()


def create_app():
    c = conf()
    app = FastAPI()
    conf_dict = asdict(c)

    # db 와 redis 설정
    db.init_app(app, **conf_dict)
    rd.init_redis(**conf_dict)

    # 데이터베이스 자동으로 만들기 (실전에선 수동으로 만들기)
    from app.router import models
    models.Base.metadata.create_all(bind=db.engine)

    # router 정의
    app.include_router(router)

    # static file 불러오기
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # 미들웨어 정의
    app.add_middleware(AccessControl, except_path_list=c.EXCEPT_PATH_LIST, except_path_regex=c.EXCEPT_PATH_REGEX)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=conf().ALLOW_SITE,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=c.TRUSTED_HOSTS, except_path=["/health"])

    return app


templates = Jinja2Templates(directory="app/templates")
app = create_app()
