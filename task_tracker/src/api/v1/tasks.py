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
from task_tracker.src.api.dependencies import SessionDep
from task_tracker.src.events.producer import send_task_lifecycle_event
from task_tracker.src.events.producer import send_task_streaming_event
from task_tracker.src.events.task_lifecycle import TaskAssigned
from task_tracker.src.events.task_lifecycle import TaskCompleted
from task_tracker.src.events.task_lifecycle import TaskCreated
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
        .order_by(Task.id.desc())
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
        .order_by(Task.id.desc())
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

    await send_task_streaming_event(task)
    await send_task_lifecycle_event(task, TaskCompleted)

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
    jira_id: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
):
    if '[' in title or ']' in title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Jira id in title')

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
        jira_id=jira_id,
        title=title,
        description=description,
        status=TaskStatus.IN_PROGRESS,
        creator_id=request.user.id,
        executor_id=random_executor.id,
    )
    db.add(task)
    await db.commit()

    task.executor = random_executor

    await send_task_streaming_event(task)
    await send_task_lifecycle_event(task, TaskCreated)
    await send_task_lifecycle_event(task, TaskAssigned)

    return RedirectResponse(request.url_for('get_all_tasks'), status_code=status.HTTP_303_SEE_OTHER)


@router.post('/assign/')
async def assign_tasks(db: SessionDep, request: Request):
    result = await db.execute(select(Task).where(Task.status == TaskStatus.IN_PROGRESS))
    tasks = result.scalars().all()
    for task in tasks:
        result = await db.execute(
            select(User)
            .where(
                User.is_active == True,
                User.role.notin_([Role.ADMIN, Role.MANAGER]),
            )
            .order_by(func.random())
            .limit(1)
        )
        executor = result.scalar()
        task.executor_id = executor.id
        task.executor = executor

    await db.flush(tasks)
    await db.commit()

    for task in tasks:
        await send_task_lifecycle_event(task, TaskAssigned)

    return RedirectResponse(request.url_for('get_all_tasks'), status_code=status.HTTP_303_SEE_OTHER)
