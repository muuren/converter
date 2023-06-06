from functools import lru_cache

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import app.auth.config as cfg
from app.auth.dao import AuthDao
from app.auth.orm import register_mapping
from app.auth.security import JWTToken, BaseAuth, Argon2Auth


@lru_cache(maxsize=1)
def get_auth_provider() -> BaseAuth:
    return Argon2Auth()


@lru_cache(maxsize=1)
def get_token_provider() -> JWTToken:
    config = cfg.JWTConfig()
    return JWTToken(config=config)


@lru_cache(maxsize=1)
def get_dao_provider() -> AuthDao:
    options = {
        "server_settings": {"application_name": cfg.PostgresConfig().app_name}
    }
    engine = create_async_engine(
        cfg.PostgresConfig().url, connect_args=options, echo=False
    )
    pool = async_sessionmaker(engine, expire_on_commit=False)
    return AuthDao(pool)


def map_orm():
    return register_mapping()
