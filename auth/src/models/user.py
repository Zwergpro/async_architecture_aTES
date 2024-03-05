import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from starlette.authentication import BaseUser

from auth.src.db import Base
from packages.permissions.role import Role


class User(BaseUser, Base):
    __tablename__ = 'auth__user'

    id: Mapped[int] = mapped_column(init=False, autoincrement=True, primary_key=True)
    public_id: Mapped[sa.UUID] = mapped_column(
        sa.types.UUID,
        unique=True,
        init=False,
        server_default=sa.text('gen_random_uuid()'),
    )
    username: Mapped[str] = mapped_column(sa.String(length=256), unique=True)
    password_hash: Mapped[str] = mapped_column(sa.String(256))
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default_factory=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )

    role: Mapped[Role] = mapped_column(default=Role.EMPLOYEE)

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
