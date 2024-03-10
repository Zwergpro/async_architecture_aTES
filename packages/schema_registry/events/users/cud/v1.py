import uuid

from pydantic import BaseModel
from pydantic import ConfigDict

from packages.permissions.role import Role


class UserCUD(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: uuid.UUID
    username: str
    is_active: bool
    role: Role
