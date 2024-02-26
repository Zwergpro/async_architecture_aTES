from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.src.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar()

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar()

    async def create_user(self, username: str, password_hash: str) -> User:
        user = await self.get_user_by_username(username)
        if user:
            raise Exception

        user = User(
            username=username,
            password_hash=password_hash,
            is_active=True,
        )
        self.db.add(user)
        await self.db.commit()
        return user

    async def get_all(self) -> Sequence[User]:
        result = await self.db.execute(select(User).order_by(User.id))
        return result.scalars().fetchall()
