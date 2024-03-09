import datetime
import enum
import random

from sqlalchemy import UUID
from sqlalchemy import String
from sqlalchemy import types
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from accounting.src.db import Base


class TaskStatus(enum.StrEnum):
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    DELETED = 'DELETED'


class Task(Base):
    __tablename__ = 'tracker__task'

    id: Mapped[int] = mapped_column(init=False, autoincrement=True, primary_key=True)
    public_id: Mapped[UUID] = mapped_column(types.UUID, unique=True)

    title: Mapped[str]
    description: Mapped[str]
    jira_id: Mapped[str] = mapped_column(String(30), default='', server_default='')
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.IN_PROGRESS)

    assign_price: Mapped[int] = mapped_column(default_factory=lambda: random.randint(10, 20))
    complete_price: Mapped[int] = mapped_column(default_factory=lambda: random.randint(20, 40))

    created_at: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default_factory=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )
    completed_at: Mapped[datetime.datetime | None] = mapped_column(default=None)
