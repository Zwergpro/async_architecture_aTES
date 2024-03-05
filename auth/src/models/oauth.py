import time
import typing

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from auth.src.db import Base

if typing.TYPE_CHECKING:
    from .user import User


class OAuthClient(Base):
    __tablename__ = 'oauth__client'

    id: Mapped[int] = mapped_column(init=False, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(256), unique=True)
    client_id: Mapped[str] = mapped_column(String(48), index=True, unique=True)
    client_secret: Mapped[str] = mapped_column(String(120))
    redirect_url: Mapped[str]


class OAuthAuthorizationCode(Base):
    __tablename__ = 'oauth__code'

    id: Mapped[int] = mapped_column(init=False, autoincrement=True, primary_key=True)
    code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    auth_time: Mapped[int] = mapped_column(default_factory=lambda: int(time.time()))

    client_id: Mapped[int] = mapped_column(
        ForeignKey('oauth__client.id', ondelete='CASCADE'),
        nullable=False,
        default=None,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('auth__user.id', ondelete='CASCADE'),
        nullable=False,
        default=None,
    )

    client: Mapped['OAuthClient'] = relationship('OAuthClient', default=None)
    user: Mapped['User'] = relationship('User', default=None)

    def is_expired(self):
        return self.auth_time + 300 < time.time()
