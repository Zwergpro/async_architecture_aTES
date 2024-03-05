import uuid

from pydantic import BaseModel

from packages.permissions.role import Role


class User(BaseModel):
    public_id: uuid.UUID
    username: str
    is_active: bool
    role: Role
