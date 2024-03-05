import enum

from pydantic import BaseModel
from pydantic import ConfigDict


class TaskStatus(enum.StrEnum):
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    DELETED = 'DELETED'


class TaskCUD(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: TaskStatus


class TaskCreated(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str


class TaskAssigned(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    executor_id: int


class TaskCompleted(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    executor_id: int
