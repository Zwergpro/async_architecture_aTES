from typing import Annotated
from typing import Generator

from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from task_tracker.src.db import session_maker
from task_tracker.src.models import User
from task_tracker.src.repositories.user import UserRepository


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
