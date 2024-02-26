import datetime
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from auth.src.api.dependencies import SessionDep
from auth.src.events.producer import send_event
from auth.src.repositories.user import UserRepository
from auth.src.services.auth.beckend import authenticate_user
from auth.src.services.auth.beckend import get_password_hash
from packages.schema_registry.events.user import UserCreated
from packages.schema_registry.events.user import UserCUD

router = APIRouter()
templates = Jinja2Templates(directory='auth/src/templates/')


@router.get('/login/', response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(request=request, name='auth/login.html')


@router.post('/login/')
async def login(
    db: SessionDep,
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    next_url: str | None = Query(alias='next', default=None),
    client_id: str | None = Query(default=None),
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
        )

    redirect_url = next_url or request.url_for('users_list')
    if client_id:
        redirect_url = f'{redirect_url}?client_id={client_id}'

    response = RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    request.session['username'] = user.username
    request.session['exp'] = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=5)
    return response


@router.get('/logout/')
async def logout(request: Request):
    request.session['username'] = None
    return RedirectResponse(
        request.url_for('login'),
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )


@router.get('/signup/', response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse(request=request, name='auth/signup.html')


@router.post('/signup/')
async def signup(
    db: SessionDep,
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    next_url: str = Query(alias='next', default=None),
):
    user = await UserRepository(db).create_user(username, get_password_hash(password))

    redirect_url = next_url or request.url_for('users_list')

    await send_event(
        topic='user.streaming',
        value=UserCUD.from_orm(user).json(),
        key=str(user.id),
    )

    await send_event(
        topic='auth.user-created',
        value=UserCreated.from_orm(user).json(),
        key=str(user.id),
    )

    request.session['username'] = user.username
    request.session['exp'] = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=5)
    return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
