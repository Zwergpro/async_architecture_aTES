import enum
import uuid

from pydantic import BaseModel
from pydantic import ConfigDict

from packages.permissions.role import Role


class UserLifecycleEventType(enum.StrEnum):
    CREATED = 'CREATED'


class UserLifecycle(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: UserLifecycleEventType
    public_id: uuid.UUID
    username: str
    role: Role
