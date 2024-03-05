import datetime
import enum
import typing

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from task_tracker.src.db import Base

if typing.TYPE_CHECKING:
    from .user import User


class TaskStatus(enum.StrEnum):
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    DELETED = 'DELETED'


class Task(Base):
    __tablename__ = 'tracker__task'

    executor_id: Mapped[int] = mapped_column(ForeignKey('auth__user.id', ondelete='CASCADE'))
    executor: Mapped['User'] = relationship(
        primaryjoin='and_(Task.executor_id == User.id)',
        init=False,
    )

    creator_id: Mapped[int] = mapped_column(ForeignKey('auth__user.id', ondelete='CASCADE'))
    creator: Mapped['User'] = relationship(
        primaryjoin='and_(Task.creator_id == User.id)',
        init=False,
    )

    id: Mapped[int] = mapped_column(init=False, autoincrement=True, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.IN_PROGRESS)

    created_at: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default_factory=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )
    completed_at: Mapped[datetime.datetime | None] = mapped_column(default=None)
