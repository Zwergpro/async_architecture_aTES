import asyncio
import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from accounting.src.models import BillingCycle


class BillingCycleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_active_for_account(self, account_id: int) -> BillingCycle:
        async with asyncio.Lock():
            result = await self.db.execute(
                select(BillingCycle)
                .where(
                    BillingCycle.account_id == account_id,
                    BillingCycle.end_dt.is_(None),
                )
                .order_by(BillingCycle.id)
            )
            billing_cycle = result.scalar()
            if not billing_cycle:
                billing_cycle = BillingCycle(account_id=account_id)
                self.db.add(billing_cycle)
                await self.db.flush()

        return billing_cycle

    async def get_active_for_account(self, account_id: int) -> BillingCycle | None:
        result = await self.db.execute(
            select(BillingCycle)
            .where(
                BillingCycle.account_id == account_id,
                BillingCycle.end_dt.is_(None),
            )
            .order_by(BillingCycle.id)
        )
        return result.scalar()

    async def get_all_active(self) -> Sequence[BillingCycle]:
        result = await self.db.execute(
            select(BillingCycle)
            .where(
                BillingCycle.end_dt.is_(None),
            )
            .options(joinedload(BillingCycle.account))
            .order_by(BillingCycle.id)
        )
        return result.scalars().all()

    async def complete_billing_cycle(self, cycle_id: int):
        await self.db.execute(
            update(BillingCycle)
            .where(
                BillingCycle.id == cycle_id,
                BillingCycle.end_dt.is_(None),
            )
            .values(end_dt=datetime.datetime.now())
        )
