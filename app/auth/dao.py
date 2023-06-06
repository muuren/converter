from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.auth.orm import users_table, pwdhashes_table


class AuthDao:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self.pool = sessionmaker

    async def get_pwdhash_value(self, user_id: int) -> str:
        expr = select(pwdhashes_table.c.value).where(
            pwdhashes_table.c.user_id == user_id
        )
        async with self.pool() as session:
            user_coro = await session.execute(expr)
            return user_coro.scalar()  # type: ignore

    async def add_one(self, item) -> int:
        async with self.pool() as session:
            session.add(item)
            await session.commit()
            return item.id

    async def add_all(self, items: list) -> list:
        async with self.pool() as session:
            session.add_all(items)
            await session.commit()
            return items

    async def get_user_id(self, email: str) -> Optional[int]:
        expr = select(users_table.c.id).where(users_table.c.email == email)
        async with self.pool() as session:
            user_id_coro = await session.execute(expr)
            return user_id_coro.scalar()
