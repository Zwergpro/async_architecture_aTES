from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from packages.auth.beckend import SessionAuthBackend
from packages.auth.middlewares import SessionMiddleware
from task_tracker.src import api
from task_tracker.src.conf import settings
from task_tracker.src.events.consumer import router as kafka_router
from task_tracker.src.services.auth.beckend import redirect_on_auth_error
from task_tracker.src.services.auth.beckend import user_getter

app = FastAPI(lifespan=kafka_router.lifespan_context)

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
    session_cookie='tracker_session',
    secret_key=settings.SECRET_KEY,
    jwt_algorithm=settings.JWT_ALGORITHM,
)


app.include_router(api.api_router)
app.include_router(kafka_router)


@app.get('/')
async def main(request: Request):
    return RedirectResponse(request.url_for('get_all_tasks'))
