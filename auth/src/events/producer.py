from aiokafka import AIOKafkaProducer

from auth.src.models import User
from packages.schema_registry import SchemaRegistry

from .user_lifecycle import UserLifecycle

BOOTSTRAP_SERVERS = 'kafka:9092'


async def send_event(
    topic: str,
    value: bytes,
    key: str | None = None,
    version: int = 1,
):
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)

    async with producer:
        result = await producer.send_and_wait(
            topic=topic,
            value=value,
            key=key.encode() if key else None,
            headers=[('version', str(version).encode())],
        )
        print(f'{result=}')


async def send_user_streaming_event(user: User):
    await send_event(
        topic='user.streaming',
        value=SchemaRegistry.serialize(user, schema_name='user.streaming', version=1),
        key=str(user.id),
        version=1,
    )


async def send_user_lifecycle_event(
    user: User,
    event_type: type[UserLifecycle],
):
    data = event_type.from_orm(user)
    await send_event(
        topic='user.lifecycle',
        value=SchemaRegistry.serialize(data, schema_name='user.lifecycle', version=1),
        key=str(user.id),
        version=1,
    )
