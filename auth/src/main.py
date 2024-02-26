from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.authentication import AuthenticationMiddleware

from auth.src import api
from auth.src.conf import settings
from auth.src.services.auth.beckend import redirect_on_auth_error
from auth.src.services.auth.beckend import user_getter
from packages.auth.beckend import SessionAuthBackend
from packages.auth.middlewares import SessionMiddleware

app = FastAPI()

app.add_middleware(
    AuthenticationMiddleware,
    backend=SessionAuthBackend(
        user_getter=user_getter,
        exclude_url_prefix=settings.AUTH_EXCLUDE_URL_PREFIX,
    ),
    on_error=redirect_on_auth_error,
)
app.add_middleware(
    SessionMiddleware,
    session_cookie='auth_session',
    secret_key=settings.SECRET_KEY,
    jwt_algorithm=settings.JWT_ALGORITHM,
)

app.include_router(api.api_router)


@app.get('/')
async def main(request: Request):
    return RedirectResponse(request.url_for('users_list'))
