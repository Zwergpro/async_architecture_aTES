from fastapi import APIRouter

from accounting.src.api.dependencies import CurrentUser
from accounting.src.schemas.auth import User

router = APIRouter()


@router.get('/me/', response_model=User)
async def about_me(user: CurrentUser):
    return user
