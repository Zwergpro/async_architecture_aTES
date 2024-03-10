from typing import Annotated
from typing import Callable
from typing import Generator

from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from accounting.src.db import session_maker
from accounting.src.models import User
from accounting.src.repositories.user import UserRepository
from packages.permissions.role import Role


async def get_db() -> Generator:
    async with session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(db: SessionDep, request: Request) -> User:
    user = await UserRepository(db).get_user_by_username(request.session['username'])

    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if not user.is_active:
        raise HTTPException(status_code=400, detail='Inactive user')
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def check_permissions(*roles: Role) -> Callable[[CurrentUser], None]:
    def func(user: CurrentUser):
        if user.role == Role.ADMIN:
            return

        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You do not have permission to access this resource',
            )

    return func
