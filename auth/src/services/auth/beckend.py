from fastapi.requests import HTTPConnection
from fastapi.responses import RedirectResponse
from fastapi.responses import Response
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from auth.src.conf import settings
from auth.src.db import session_maker
from auth.src.models import User
from auth.src.repositories.user import UserRepository

pwd_context = CryptContext(schemes=[settings.CRYPT_CONTEXT_SCHEMA])


async def user_getter(username: str) -> User:
    async with session_maker() as session:
        user = await UserRepository(session).get_user_by_username(username)
    return user


def redirect_on_auth_error(conn: HTTPConnection, exc: Exception) -> Response:
    response = RedirectResponse(f'/v1/auth/login/?next={conn.url.path}', status_code=307)
    response.delete_cookie('session')
    return response


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    user = await UserRepository(db).get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
