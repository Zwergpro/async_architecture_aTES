from typing import Awaitable
from typing import Callable

from fastapi.requests import HTTPConnection
from starlette.authentication import AuthenticationBackend
from starlette.authentication import AuthenticationError
from starlette.authentication import BaseUser


class SessionAuthBackend(AuthenticationBackend):
    def __init__(
        self,
        user_getter: Callable[[str], Awaitable[BaseUser]],
        exclude_url_prefix: list[str],
    ):
        self.user_getter = user_getter
        self.exclude_url_prefix = exclude_url_prefix

    async def authenticate(self, conn: HTTPConnection):
        username: str = conn.session.get('username')

        if not username:
            if not any(conn.url.path.startswith(path) for path in self.exclude_url_prefix):
                raise AuthenticationError('Invalid session.')
            return None

        user = await self.user_getter(username)
        return username, user
