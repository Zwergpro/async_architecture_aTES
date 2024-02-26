import random
import string

from fastapi import APIRouter
from fastapi import Form
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from auth.src.api.dependencies import SessionDep
from auth.src.models import OAuthAuthorizationCode
from auth.src.models import OAuthClient
from auth.src.schemas.oauth import OAuthUserInfo

router = APIRouter()
templates = Jinja2Templates(directory='auth/src/templates/')


@router.get('/grant_access/', response_class=HTMLResponse)
async def grant_access(
    db: SessionDep,
    request: Request,
    client_id: str = Query(...),
):
    clients = await db.execute(select(OAuthClient).where(OAuthClient.client_id == client_id))
    client: OAuthClient = clients.scalar()
    if not client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if not request.user.is_authenticated:  # not authenticated
        next_url = request.url_for('grant_access').path
        login_url = request.url_for('login')
        return RedirectResponse(f'{login_url}?next={next_url}&client_id={client_id}')

    return templates.TemplateResponse(
        request=request,
        name='oauth/grant_access.html',
        context={
            'client': client,
        },
    )


@router.post('/grant_access/', response_class=HTMLResponse)
async def grant_access(
    db: SessionDep,
    request: Request,
    client_id: str = Form(...),
):
    if not request.user.is_authenticated:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    clients = await db.execute(select(OAuthClient).where(OAuthClient.client_id == client_id))
    client: OAuthClient = clients.scalars().first()
    if not client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    auth_code = OAuthAuthorizationCode(
        user=request.user,
        client=client,
        code=''.join(random.choices(string.ascii_uppercase + string.digits, k=20)),
    )
    db.add(auth_code)
    await db.commit()

    return RedirectResponse(
        f'{client.redirect_url}?code={auth_code.code}',
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )


@router.post('/user_info/', response_model=OAuthUserInfo)
async def get_user_info(
    db: SessionDep,
    code: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
):
    clients = await db.execute(
        select(OAuthClient).where(
            OAuthClient.client_id == client_id,
            OAuthClient.client_secret == client_secret,
        )
    )
    client: OAuthClient = clients.scalar()
    if not client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    auth_codes = await db.execute(
        select(OAuthAuthorizationCode)
        .where(
            OAuthAuthorizationCode.client_id == client.id,
            OAuthAuthorizationCode.code == code,
        )
        .options(joinedload(OAuthAuthorizationCode.user, innerjoin=True))
    )
    auth_code: OAuthAuthorizationCode = auth_codes.scalars().first()
    if not auth_code or auth_code.is_expired():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return auth_code.user


@router.get('/clients/', response_class=HTMLResponse)
async def get_all_oauth_clients(db: SessionDep, request: Request):
    clients = await db.execute(select(OAuthClient).order_by(OAuthClient.id))
    return templates.TemplateResponse(
        request=request,
        name='oauth/clients.html',
        context={
            'clients': clients.scalars().fetchall(),
        },
    )


@router.post('/clients/', response_class=HTMLResponse)
async def create_oauth_client(
    db: SessionDep,
    request: Request,
    name: str = Form(...),
    redirect_url: str = Form(...),
):
    client = OAuthClient(
        name=name,
        redirect_url=redirect_url,
        client_id=''.join(random.choices(string.ascii_uppercase + string.digits, k=5)),
        client_secret=''.join(random.choices(string.ascii_uppercase + string.digits, k=10)),
    )
    db.add(client)
    await db.commit()

    return RedirectResponse(
        request.url_for('get_all_oauth_clients'),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post('/clients/{client_id}/', response_class=HTMLResponse)
async def delete_oauth_client(
    db: SessionDep,
    request: Request,
    client_id: int,
):
    clients = await db.execute(select(OAuthClient).where(OAuthClient.id == client_id))
    client = clients.scalars().first()

    if not client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    await db.delete(client)
    await db.commit()

    return RedirectResponse(
        request.url_for('get_all_oauth_clients'),
        status_code=status.HTTP_303_SEE_OTHER,
    )
