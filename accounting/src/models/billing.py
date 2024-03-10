import datetime
import decimal
import typing

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from accounting.src.db import Base

if typing.TYPE_CHECKING:
    from accounting.src.models import Task
    from accounting.src.models import User


class Account(Base):
    __tablename__ = 'accounting__account'

    user_id: Mapped[int] = mapped_column(ForeignKey('auth__user.id', ondelete='CASCADE'))
    user: Mapped['User'] = relationship(
        primaryjoin='and_(Account.user_id == User.id)',
        init=False,
    )

    id: Mapped[int] = mapped_column(init=False, autoincrement=True, primary_key=True)
    balance: Mapped[decimal.Decimal] = mapped_column(default=0)


class Transaction(Base):
    __tablename__ = 'accounting__transaction'

    account_id: Mapped[int] = mapped_column(
        ForeignKey('accounting__account.id', ondelete='CASCADE')
    )
    billing_cycle_id: Mapped[int] = mapped_column(
        ForeignKey('accounting__billing_cycle.id', ondelete='CASCADE')
    )
    task_id: Mapped[int | None] = mapped_column(
        ForeignKey('tracker__task.id', ondelete='CASCADE'),
        default=None,
    )

    id: Mapped[int] = mapped_column(init=False, autoincrement=True, primary_key=True)

    description: Mapped[str] = mapped_column(default='')
    processing_dt: Mapped[datetime.datetime] = mapped_column(
        default_factory=datetime.datetime.now,
    )
    credit: Mapped[decimal.Decimal] = mapped_column(default=0)
    debit: Mapped[decimal.Decimal] = mapped_column(default=0)

    account: Mapped['Account'] = relationship(
        primaryjoin='and_(Transaction.account_id == Account.id)',
        init=False,
    )
    billing_cycle: Mapped['BillingCycle'] = relationship(
        primaryjoin='and_(Transaction.billing_cycle_id == BillingCycle.id)',
        init=False,
    )
    task: Mapped[typing.Optional['Task']] = relationship(
        primaryjoin='and_(Transaction.task_id == Task.id)',
        init=False,
    )


class BillingCycle(Base):
    __tablename__ = 'accounting__billing_cycle'

    account_id: Mapped[int] = mapped_column(
        ForeignKey('accounting__account.id', ondelete='CASCADE')
    )

    id: Mapped[int] = mapped_column(init=False, autoincrement=True, primary_key=True)
    start_dt: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    end_dt: Mapped[datetime.datetime | None] = mapped_column(default=None)

    account: Mapped['Account'] = relationship(
        primaryjoin='and_(BillingCycle.account_id == Account.id)',
        init=False,
    )
