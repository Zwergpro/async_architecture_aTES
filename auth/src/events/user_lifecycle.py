from packages.schema_registry.events.users.lifecycle.v1 import UserLifecycle
from packages.schema_registry.events.users.lifecycle.v1 import UserLifecycleEventType


class UserCreated(UserLifecycle):
    type: UserLifecycleEventType = UserLifecycleEventType.CREATED
