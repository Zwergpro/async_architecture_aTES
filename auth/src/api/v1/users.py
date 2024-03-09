from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.responses import HTMLResponse
from starlette.responses import RedirectResponse

from auth.src.api.dependencies import SessionDep
from auth.src.api.dependencies import check_permissions
from auth.src.events.producer import send_user_streaming_event
from auth.src.repositories.user import UserRepository
from auth.src.schemas.auth import User
from packages.permissions.role import Role

router = APIRouter()
templates = Jinja2Templates(directory='auth/src/templates/')


@router.get('/', response_class=HTMLResponse)
async def users_list(db: SessionDep, request: Request):
    users = await UserRepository(db).get_all()
    return templates.TemplateResponse(
        request=request,
        name='users/users.html',
        context={'users': users},
    )


@router.post(
    '/{user_id}/activity/',
    dependencies=[Depends(check_permissions(Role.ADMIN))],
)
async def change_user_activity(
    db: SessionDep,
    user_id: int,
    request: Request,
    is_active: str = Form(...),
):
    user = await UserRepository(db).get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user.is_active = is_active == 'True'
    await db.flush([user])
    await db.commit()

    await send_user_streaming_event(user)

    return RedirectResponse(request.url_for('users_list'), status_code=status.HTTP_303_SEE_OTHER)


@router.post(
    '/{user_id}/role/',
    response_model=User,
    dependencies=[Depends(check_permissions(Role.ADMIN))],
)
async def update_user_role(
    db: SessionDep, user_id: int, request: Request, role: Role = Form(multiple_o=Role)
):
    user = await UserRepository(db).get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user.role = role
    await db.flush([user])
    await db.commit()

    await send_user_streaming_event(user)

    return RedirectResponse(request.url_for('users_list'), status_code=status.HTTP_303_SEE_OTHER)
