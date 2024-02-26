from fastapi import APIRouter

from task_tracker.src.api.dependencies import CurrentUser
from task_tracker.src.schemas.auth import User

router = APIRouter()


@router.get('/me/', response_model=User)
async def about_me(user: CurrentUser):
    return user
