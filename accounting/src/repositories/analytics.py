import datetime
from typing import Sequence

from sqlalchemy import Row
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_earned_today(self) -> int:
        result = await self.db.execute(
            text("""
            select sum(t.credit) - sum(t.debit)
            from accounting__transaction as t
            where t.processing_dt::date = now()::date and task_id is not null
        """)
        )
        return result.scalar() or 0

    async def get_workers_count_with_negative_balance(self) -> int:
        result = await self.db.execute(
            text("""
            with accout_amount as (
                select t.account_id, sum(t.credit) - sum(t.debit) as amount
                from accounting__transaction as t
                where t.processing_dt::date = now()::date
                group by t.account_id
            )
            select count(account_id)
            from accout_amount
            where amount > 0
        """)
        )
        return result.scalar() or 0

    async def get_most_expensive_task_per_day(
        self,
    ) -> Sequence[Row[tuple[datetime.datetime, datetime.datetime, int]]]:
        result = await self.db.execute(
            text("""
            select completed_at::date, max(complete_price)
            from tracker__task
            where completed_at::date between now() - interval '30 days' and now()::date
            group by completed_at::date
            order by completed_at::date desc
        """)
        )
        return result.fetchall()

    async def get_most_expensive_task_per_week(
        self,
    ) -> Sequence[Row[tuple[datetime.datetime, datetime.datetime, int]]]:
        result = await self.db.execute(
            text("""
            select
                date_trunc('week', completed_at)::date,
                (date_trunc('week', completed_at)::date + interval '6 days')::date,
                max(complete_price)
            from tracker__task
            where completed_at::date between now() - interval '30 days' and now()::date
            group by 
                date_trunc('week', completed_at)::date,
                (date_trunc('week', completed_at)::date + interval '7 days')::date
            order by date_trunc('week', completed_at)::date desc
        """)
        )
        return result.fetchall()

    async def get_most_expensive_task_last_month(
        self,
    ) -> Sequence[Row[tuple[datetime.datetime, datetime.datetime, int]]]:
        result = await self.db.execute(
            text("""
            select
                date_trunc('month', completed_at)::date,
                (date_trunc('month', completed_at)::date + interval '30 days')::date,
                max(complete_price)
            from tracker__task
            where date_trunc('month', completed_at)::date = date_trunc('month', now())::date
            group by
                date_trunc('month', completed_at),
                (date_trunc('month', completed_at)::date + interval '30 days')::date
            order by date_trunc('month', completed_at) desc
        """)
        )
        return result.fetchall()
