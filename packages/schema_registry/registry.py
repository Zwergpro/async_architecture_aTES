from typing import Any

from pydantic import BaseModel

import packages.schema_registry.events.tasks.cud.v1 as task_cud_v1
import packages.schema_registry.events.tasks.cud.v2 as task_cud_v2
import packages.schema_registry.events.tasks.lifecycle.v1 as task_lifecycle_v1
import packages.schema_registry.events.users.cud.v1 as users_cud_v1
import packages.schema_registry.events.users.lifecycle.v1 as users_lifecycle_v1

SCHEMA_REGISTRY = {
    'task': {
        'streaming': {
            1: task_cud_v1.TaskCUD,
            2: task_cud_v2.TaskCUD,
        },
        'lifecycle': {
            1: task_lifecycle_v1.TaskLifecycle,
        },
    },
    'user': {
        'lifecycle': {
            1: users_lifecycle_v1.UserLifecycle,
        },
        'streaming': {
            1: users_cud_v1.UserCUD,
        },
    },
}


class SchemaRegistry:
    @staticmethod
    def serialize(
        data: Any,
        schema_name: str,
        version: int,
    ) -> bytes:
        entity, event = schema_name.split('.')
        schema: type[BaseModel] = SCHEMA_REGISTRY[entity][event][version]
        return schema.from_orm(data).model_dump_json().encode()

    @staticmethod
    def deserialize(
        data: bytes,
        schema_name: str,
        version: int,
    ) -> BaseModel:
        entity, event = schema_name.split('.')
        schema: type[BaseModel] = SCHEMA_REGISTRY[entity][event][version]
        return schema.parse_raw(data)
