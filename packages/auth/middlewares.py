import typing

from jose import JWTError
from jose import jwt
from starlette.datastructures import MutableHeaders
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp
from starlette.types import Message
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send


class SessionMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        secret_key: str,
        jwt_algorithm: str,
        path: str = '/',
        same_site: typing.Literal['lax', 'strict', 'none'] = 'lax',
        https_only: bool = False,
        domain: typing.Optional[str] = None,
        session_cookie: str = 'session',
        max_age: int = 5 * 24 * 60 * 60,  # 5 days, in seconds
    ) -> None:
        self.app = app
        self.path = path
        self.security_flags = 'httponly; samesite=' + same_site
        if https_only:  # Secure flag can be used with HTTPS only
            self.security_flags += '; secure'
        if domain is not None:
            self.security_flags += f'; domain={domain}'

        self.session_cookie = session_cookie
        self.max_age = max_age
        self.secret_key = secret_key
        self.jwt_algorithm = jwt_algorithm

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] not in ('http', 'websocket'):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)
        initial_session_was_empty = True

        if self.session_cookie in connection.cookies:
            data = connection.cookies[self.session_cookie]
            try:
                scope['session'] = jwt.decode(
                    data, self.secret_key, algorithms=[self.jwt_algorithm]
                )
                initial_session_was_empty = False
            except JWTError:
                scope['session'] = {}
        else:
            scope['session'] = {}

        async def send_wrapper(message: Message) -> None:
            if message['type'] == 'http.response.start':
                if scope['session']:
                    # We have session data to persist.
                    headers = MutableHeaders(scope=message)
                    header_value = (
                        '{session_cookie}={data}; path={path}; {max_age}{security_flags}'.format(  # noqa E501
                            session_cookie=self.session_cookie,
                            data=jwt.encode(
                                scope['session'],
                                self.secret_key,
                                algorithm=self.jwt_algorithm,
                            ),
                            path=self.path,
                            max_age=f'Max-Age={self.max_age}; ' if self.max_age else '',
                            security_flags=self.security_flags,
                        )
                    )
                    headers.append('Set-Cookie', header_value)
                elif not initial_session_was_empty:
                    # The session has been cleared.
                    headers = MutableHeaders(scope=message)
                    header_value = (
                        '{session_cookie}={data}; path={path}; {expires}{security_flags}'.format(  # noqa E501
                            session_cookie=self.session_cookie,
                            data='null',
                            path=self.path,
                            expires='expires=Thu, 01 Jan 1970 00:00:00 GMT; ',
                            security_flags=self.security_flags,
                        )
                    )
                    headers.append('Set-Cookie', header_value)
            await send(message)

        await self.app(scope, receive, send_wrapper)
