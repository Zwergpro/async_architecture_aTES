from fastapi import APIRouter

from accounting.src.api.v1 import billing
from accounting.src.api.v1 import oauth
from accounting.src.api.v1 import users

api_router = APIRouter(prefix='/v1')

api_router.include_router(oauth.router, prefix='/oauth', tags=['oauth'])
api_router.include_router(users.router, prefix='/users', tags=['users'])
api_router.include_router(billing.router, prefix='/billing', tags=['billing'])
