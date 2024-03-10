import asyncio
import decimal
import logging
import sys

from sqlalchemy import text
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from accounting.src.models import Account
from accounting.src.models import BillingCycle
from accounting.src.models import Task
from accounting.src.models import Transaction
from accounting.src.models import User
from accounting.src.models.task import TaskStatus
from accounting.src.repositories.account import AccountRepository
from accounting.src.repositories.billing_cycle import BillingCycleRepository

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.level = logging.DEBUG


async def assign_task(db: AsyncSession, task: Task, executor: User) -> Transaction:
    if task.status != TaskStatus.IN_PROGRESS:
        raise Exception

    account = await AccountRepository(db).get_user_account(executor.id)
    billing_cycle = await BillingCycleRepository(db).get_or_create_active_for_account(account.id)

    transaction = Transaction(
        credit=task.assign_price,
        account_id=account.id,
        task_id=task.id,
        billing_cycle_id=billing_cycle.id,
        description=f'Assigned on Task:{task.id}',
    )
    db.add(transaction)
    await db.flush()

    await db.execute(
        update(Account)
        .where(Account.id == account.id)
        .values(balance=Account.balance - transaction.credit)
    )

    return transaction


async def complete_task(db: AsyncSession, task: Task, executor: User) -> Transaction:
    if task.status in (TaskStatus.DONE, TaskStatus.DELETED):
        raise Exception

    account = await AccountRepository(db).get_user_account(executor.id)
    billing_cycle = await BillingCycleRepository(db).get_or_create_active_for_account(account.id)

    transaction = Transaction(
        debit=task.complete_price,
        account_id=account.id,
        task_id=task.id,
        billing_cycle_id=billing_cycle.id,
        description=f'Completed Task:{task.id}',
    )
    db.add(transaction)
    await db.flush()

    await db.execute(
        update(Account)
        .where(Account.id == account.id)
        .values(balance=Account.balance + transaction.debit)
    )

    return transaction


async def complete_billing_cycles(db: AsyncSession):
    async with asyncio.Lock():
        active_billing_cycles = await BillingCycleRepository(db).get_all_active()

        for cycle in active_billing_cycles:
            async with db.begin_nested():
                try:
                    await _complete_billing_cycle(db, cycle)
                except Exception:
                    await db.rollback()
                    logger.exception('Can not process %s billing cycle', cycle.id)
                else:
                    await db.flush()

        await db.commit()


async def _complete_billing_cycle(db: AsyncSession, cycle: BillingCycle):
    result = await db.execute(
        text("""
                        select sum(t.debit) - sum(t.credit)
                        from accounting__transaction as t
                        where t.billing_cycle_id = :billing_cycle_id
                    """),
        {'billing_cycle_id': cycle.id},
    )
    amount: decimal.Decimal = result.scalar()

    if amount <= 0:
        logger.info(
            'Can not complete %s cycle for account %s with amount %s у.е.',
            cycle.id,
            cycle.account_id,
            amount,
        )
        return

    transaction = Transaction(
        account_id=cycle.account_id,
        billing_cycle_id=cycle.id,
        description=f'Withdrawal for {cycle.account_id} account',
        credit=amount,
    )
    db.add(transaction)

    await db.execute(
        update(Account)
        .where(Account.id == cycle.account_id)
        .values(balance=Account.balance - transaction.credit)
    )

    await BillingCycleRepository(db).complete_billing_cycle(cycle.id)

    logger.info(
        'Complete %s cycle for account %s with withdrawal %s у.е.',
        cycle.id,
        cycle.account_id,
        transaction.credit,
    )
