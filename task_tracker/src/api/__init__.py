from fastapi import APIRouter

from task_tracker.src.api.v1 import oauth
from task_tracker.src.api.v1 import tasks
from task_tracker.src.api.v1 import users

api_router = APIRouter(prefix='/v1')

api_router.include_router(oauth.router, prefix='/oauth', tags=['oauth'])
api_router.include_router(users.router, prefix='/users', tags=['users'])
api_router.include_router(tasks.router, prefix='/tasks', tags=['tasks'])
