import uuid

from pydantic import BaseModel
from pydantic import ConfigDict


class TaskCUD(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: uuid.UUID
    jira_id: str
    title: str
    description: str
