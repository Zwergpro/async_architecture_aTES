import uuid

from pydantic import BaseModel


class User(BaseModel):
    public_id: uuid.UUID
    username: str
    is_active: bool
