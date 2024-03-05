from fastapi import APIRouter

from auth.src.api.v1 import auth
from auth.src.api.v1 import oauth
from auth.src.api.v1 import users

api_router = APIRouter(prefix='/v1')

api_router.include_router(auth.router, prefix='/auth', tags=['auth'])
api_router.include_router(oauth.router, prefix='/oauth', tags=['oauth'])
api_router.include_router(users.router, prefix='/users', tags=['users'])
