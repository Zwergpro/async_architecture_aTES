import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from accounting.src.models import Task


class TaskDoesNotExist(Exception):
    pass


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_public_id(self, public_id: uuid.UUID) -> Task | None:
        result = await self.db.execute(select(Task).where(Task.public_id == public_id))
        return result.scalars().first()

    async def create_task(
        self, public_id: uuid.UUID, title: str, description: str, jira_id: str = ''
    ) -> Task:
        task = await self.get_by_public_id(public_id)
        if task:
            raise Exception()

        task = Task(
            public_id=public_id,
            jira_id=jira_id,
            title=title,
            description=description,
        )
        self.db.add(task)
        await self.db.commit()
        return task
