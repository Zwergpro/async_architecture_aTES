from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from accounting.src.models import Account
from accounting.src.models import Transaction


class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_for_account(self, account_id: int) -> Sequence[Transaction]:
        result = await self.db.execute(
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .order_by(Transaction.id.desc())
        )
        return result.scalars().all()

    async def get_all_for_billing_cycle(self, billing_cycle_id: int) -> Sequence[Transaction]:
        result = await self.db.execute(
            select(Transaction)
            .where(Transaction.billing_cycle_id == billing_cycle_id)
            .order_by(Transaction.id.desc())
        )
        return result.scalars().all()

    async def get_all(self) -> Sequence[Transaction]:
        result = await self.db.execute(
            select(Transaction)
            .options(joinedload(Transaction.account).options(joinedload(Account.user)))
            .order_by(Transaction.id.desc())
        )
        return result.scalars().all()
