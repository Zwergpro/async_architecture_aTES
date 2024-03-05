import uuid

from pydantic import BaseModel

from packages.permissions.role import Role


class OAuthUserInfo(BaseModel):
    username: str
    public_id: uuid.UUID
    role: Role
