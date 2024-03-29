import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from starlette.authentication import BaseUser

from packages.permissions.role import Role
from task_tracker.src.db import Base


class User(BaseUser, Base):
    __tablename__ = 'auth__user'

    id: Mapped[int] = mapped_column(init=False, autoincrement=True, primary_key=True)
    public_id: Mapped[sa.UUID] = mapped_column(sa.types.UUID, unique=True)
    username: Mapped[str] = mapped_column(sa.String(length=256), unique=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    role: Mapped[Role] = mapped_column(default=Role.EMPLOYEE)

    created_at: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default_factory=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )

    def __repr__(self) -> str:
        return f'User: {self.username}({self.id})'

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def identity(self) -> str:
        return self.id
