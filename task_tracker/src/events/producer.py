from aiokafka import AIOKafkaProducer

from packages.schema_registry import SchemaRegistry
from task_tracker.src.models import Task

from .task_lifecycle import TaskLifecycle

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


async def send_task_streaming_event(task: Task):
    await send_event(
        topic='task.streaming',
        value=SchemaRegistry.serialize(task, schema_name='task.streaming', version=2),
        key=str(task.id),
        version=2,
    )


async def send_task_lifecycle_event(
    task: Task,
    event_type: type[TaskLifecycle],
):
    data = event_type.from_orm(task)
    await send_event(
        topic='task.lifecycle',
        value=SchemaRegistry.serialize(data, schema_name='task.lifecycle', version=1),
        key=str(task.id),
        version=1,
    )
