import enum
import uuid

from pydantic import BaseModel
from pydantic import ConfigDict


class TaskLifecycleEventType(enum.StrEnum):
    CREATED = 'CREATED'
    ASSIGNED = 'ASSIGNED'
    COMPLETED = 'COMPLETED'


class TaskLifecycle(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: TaskLifecycleEventType

    public_id: uuid.UUID
    executor_public_id: uuid.UUID | None
