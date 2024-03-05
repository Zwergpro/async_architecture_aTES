from fastapi import APIRouter
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from starlette import status

from packages.permissions.role import Role
from packages.schema_registry.events.tasks import TaskAssigned
from packages.schema_registry.events.tasks import TaskCompleted
from packages.schema_registry.events.tasks import TaskCreated
from packages.schema_registry.events.tasks import TaskCUD
from task_tracker.src.api.dependencies import SessionDep
from task_tracker.src.events.producer import send_event
from task_tracker.src.models import Task
from task_tracker.src.models import User
from task_tracker.src.models.task import TaskStatus

router = APIRouter()
templates = Jinja2Templates(directory='task_tracker/src/templates/')


@router.get('/', response_class=HTMLResponse)
async def get_all_tasks(db: SessionDep, request: Request):
    tasks = await db.execute(
        select(Task)
        .options(joinedload(Task.executor))
        .options(joinedload(Task.creator))
        .order_by(Task.id)
    )
    return templates.TemplateResponse(
        request=request,
        name='tasks/tasks.html',
        context={'tasks': tasks.scalars()},
    )


@router.get('/assign/{executor_id}/', response_class=HTMLResponse)
async def get_assigned_tasks(db: SessionDep, request: Request, executor_id: int):
    tasks = await db.execute(
        select(Task)
        .where(Task.executor_id == executor_id)
        .options(joinedload(Task.executor))
        .options(joinedload(Task.creator))
        .order_by(Task.id)
    )
    return templates.TemplateResponse(
        request=request,
        name='tasks/executor_tasks.html',
        context={'tasks': tasks.scalars()},
    )


@router.post('{task_id}/executor/{executor_id}/complete/', response_class=HTMLResponse)
async def complete_task(db: SessionDep, request: Request, executor_id: int, task_id: int):
    result = await db.execute(
        select(Task)
        .where(
            Task.id == task_id,
            Task.executor_id == executor_id,
        )
        .options(joinedload(Task.executor))
    )
    task = result.scalar()
    if not task or task.status != TaskStatus.IN_PROGRESS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    task.status = TaskStatus.DONE
    await db.flush([task])
    await db.commit()

    await send_event(
        topic='task.streaming',
        value=TaskCUD.from_orm(task).json(),
        key=str(task.id),
    )
    await send_event(
        topic='tracker.task-completed',
        value=TaskCompleted.from_orm(task).json(),
        key=str(task.id),
    )

    return RedirectResponse(
        request.url_for('get_assigned_tasks', executor_id=executor_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get('/new/', response_class=HTMLResponse)
async def create_task(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='tasks/new_task.html',
    )


@router.post('/new/')
async def create_task(
    db: SessionDep,
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
):
    result = await db.execute(
        select(User)
        .where(
            User.is_active == True,
            User.role.notin_([Role.ADMIN, Role.MANAGER]),
        )
        .order_by(func.random())
        .limit(1)
    )
    random_executor = result.scalar()
    if not random_executor:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    task = Task(
        title=title,
        description=description,
        status=TaskStatus.IN_PROGRESS,
        creator_id=request.user.id,
        executor_id=random_executor.id,
    )
    db.add(task)
    await db.commit()

    await send_event(
        topic='task.streaming',
        value=TaskCUD.from_orm(task).json(),
        key=str(task.id),
    )
    await send_event(
        topic='tracker.task-created',
        value=TaskCreated.from_orm(task).json(),
        key=str(task.id),
    )
    await send_event(
        topic='tracker.task-assigned',
        value=TaskAssigned.from_orm(task).json(),
        key=str(task.id),
    )

    return RedirectResponse(request.url_for('get_all_tasks'), status_code=status.HTTP_303_SEE_OTHER)


@router.post('/assign/')
async def assign_tasks(db: SessionDep, request: Request):
    result = await db.execute(select(Task).where(Task.status == TaskStatus.IN_PROGRESS))
    tasks = result.scalars().all()
    for task in tasks:
        result = await db.execute(
            select(User.id)
            .where(
                User.is_active == True,
                User.role.notin_([Role.ADMIN, Role.MANAGER]),
            )
            .order_by(func.random())
            .limit(1)
        )

        task.executor_id = result.scalar()

    await db.flush(tasks)
    await db.commit()

    for task in tasks:
        await send_event(
            topic='task.streaming',
            value=TaskCUD.from_orm(task).json(),
            key=str(task.id),
        )
        await send_event(
            topic='tracker.task-assigned',
            value=TaskAssigned.from_orm(task).json(),
            key=str(task.id),
        )

    return RedirectResponse(request.url_for('get_all_tasks'), status_code=status.HTTP_303_SEE_OTHER)
