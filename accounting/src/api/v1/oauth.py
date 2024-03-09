import datetime

import httpx
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import RedirectResponse

from accounting.src.api.dependencies import SessionDep
from accounting.src.conf import settings
from accounting.src.models import User
from accounting.src.repositories.user import UserRepository

router = APIRouter()


@router.get('/login/')
async def login(request: Request):
    return RedirectResponse(f'{settings.oauth.SERVICE_URL}?client_id={settings.oauth.CLIENT_ID}')


@router.post('/authorization/')
async def authorization(
    db: SessionDep,
    request: Request,
    code: str,
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.oauth.SERVICE_USER_INFO_URL,
            data={
                'client_id': settings.oauth.CLIENT_ID,
                'client_secret': settings.oauth.CLIENT_SECRET,
                'code': code,
            },
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    user_info = response.json()

    user: User | None = await UserRepository(db).get_by_public_id(user_info['public_id'])

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    request.session['username'] = user.username
    request.session['exp'] = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)
    return RedirectResponse(
        request.url_for('get_account_info'), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get('/logout/')
async def logout(request: Request):
    request.session['username'] = None
    return RedirectResponse(
        request.url_for('login'),
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )
