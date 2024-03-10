from packages.schema_registry.events.tasks.lifecycle.v1 import TaskLifecycle
from packages.schema_registry.events.tasks.lifecycle.v1 import TaskLifecycleEventType


class TaskCreated(TaskLifecycle):
    type: TaskLifecycleEventType = TaskLifecycleEventType.CREATED


class TaskAssigned(TaskLifecycle):
    type: TaskLifecycleEventType = TaskLifecycleEventType.ASSIGNED


class TaskCompleted(TaskLifecycle):
    type: TaskLifecycleEventType = TaskLifecycleEventType.COMPLETED
