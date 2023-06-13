from functools import lru_cache

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.auth.config import pg_config, jwt_config
from app.auth.dao import AuthDao
from app.auth.orm import register_mapping
from app.auth.security import JWTToken, BaseAuth, Argon2Auth


@lru_cache(maxsize=1)
def get_auth_provider() -> BaseAuth:
    return Argon2Auth()


@lru_cache(maxsize=1)
def get_token_provider() -> JWTToken:
    return JWTToken(config=jwt_config)


@lru_cache(maxsize=1)
def get_dao_provider() -> AuthDao:
    options = {
        "timeout": pg_config.timeout,
        "server_settings": {"application_name": pg_config.app_name},
    }
    engine = create_async_engine(
        pg_config.url, connect_args=options, echo=False, pool_pre_ping=True
    )
    pool = async_sessionmaker(engine, expire_on_commit=False)
    return AuthDao(pool)


def map_orm():
    return register_mapping()
