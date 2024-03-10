import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from accounting.src.models import Account
from accounting.src.models import User
from packages.permissions.role import Role


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_public_id(self, public_id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.public_id == public_id))
        return result.scalars().first()

    async def create_user(self, username: str, public_id: uuid.UUID, role: Role) -> User:
        user = await self.get_by_public_id(public_id)
        if user:
            raise Exception('User already exists')

        user = User(
            username=username,
            public_id=public_id,
            is_active=True,
            role=role,
        )
        self.db.add(user)
        await self.db.flush()

        account = Account(user_id=user.id)
        self.db.add(account)
        await self.db.flush()

        user.account = account
        return user

    async def get_all(self) -> Sequence[User]:
        result = await self.db.execute(select(User).order_by(User.uuid))
        return result.scalars().fetchall()
