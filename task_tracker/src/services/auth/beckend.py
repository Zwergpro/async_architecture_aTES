from fastapi.requests import HTTPConnection
from fastapi.responses import RedirectResponse
from fastapi.responses import Response

from task_tracker.src.db import session_maker
from task_tracker.src.models import User
from task_tracker.src.repositories.user import UserRepository


def redirect_on_auth_error(conn: HTTPConnection, exc: Exception) -> Response:
    response = RedirectResponse('/v1/oauth/login/', status_code=307)
    response.delete_cookie('session')
    return response


async def user_getter(username: str) -> User:
    async with session_maker() as session:
        user = await UserRepository(session).get_user_by_username(username)
    return user
