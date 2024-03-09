from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from accounting.src.models import Account


class AccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_account(self, user_id: int) -> Account | None:
        result = await self.db.execute(select(Account).where(Account.user_id == user_id))
        return result.scalars().first()
