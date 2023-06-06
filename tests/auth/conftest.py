from typing import Optional

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import TextClause, create_engine
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker, clear_mappers

from app.auth.app import app
from app.auth.config import JWTConfig, PostgresConfig
from app.auth.dao import AuthDao
from app.auth.models import PWDHash, User
from app.auth.orm import metadata, register_mapping
from app.auth.schema import UserCredentials
from app.auth.security import JWTToken, Argon2Auth


# UNIT:

class FakeAuthDao(AuthDao):
    def __init__(self, data: dict):
        self.db = data

    async def get_user_id(self, email: str) -> Optional[int]:
        for user in self.db:
            if user[1].email == email:
                return user[0]

    async def get_pwdhash_value(self, user_id: int) -> str:
        for pwd in self.db.values():
            if pwd[1].user_id == user_id:
                return pwd[1].value

    async def add_one(self, item) -> int:
        return 1


@pytest.fixture(scope="module")
def auth_tokenizer():
    config = JWTConfig()
    return JWTToken(config=config)


@pytest.fixture(scope="module")
def user_form_data() -> UserCredentials:
    return UserCredentials(email="test@email.com", password="121212")


@pytest.fixture(scope="module")
def new_user_form_data() -> UserCredentials:
    return UserCredentials(email="unknown@email.com", password="123456789")


@pytest.fixture(scope="function")
def fake_dao():
    test_data = {
        (12, User("test@email.com")): (
            1,
            PWDHash(value=Argon2Auth.hash_password("121212"), user_id=12),
        ),
        (13, User("test13@email.com")): (
            2,
            PWDHash(value=Argon2Auth.hash_password("131313"), user_id=13),
        ),
    }
    return FakeAuthDao(test_data)


@pytest.fixture(scope="module")
def test_auth():
    return Argon2Auth()


# INTEGRATION:

@pytest.fixture
def mappers():
    register_mapping()
    yield
    clear_mappers()


@pytest.mark.asyncio
async def recreate_tables(engine: AsyncEngine, schema):
    stmt = f"attach ':memory:' as {schema}"
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.execute(TextClause(stmt))
        await conn.run_sync(metadata.create_all)


@pytest_asyncio.fixture
async def auth_dao():
    engine = create_async_engine(url="sqlite+aiosqlite:///")
    await recreate_tables(engine, schema="test")
    pool = async_sessionmaker(bind=engine, expire_on_commit=False)
    yield AuthDao(pool)


# E2E:

@pytest.fixture
def test_tables_teardown():
    conf = PostgresConfig(schema="test", driver="postgresql")
    engine = create_engine(url=conf.url)
    metadata.create_all(bind=engine)
    yield
    metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def test_app():
    with TestClient(app) as test_client:
        yield test_client


# manual session call for console playground
def create_in_memory_session():
    pgconfig = PostgresConfig()
    stmt = f"attach ':memory:' as {pgconfig.schema}"
    engine = create_engine(url="sqlite:///")
    register_mapping()
    metadata.drop_all(engine)
    with engine.begin() as conn:
        conn.execute(TextClause(stmt))
    metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
