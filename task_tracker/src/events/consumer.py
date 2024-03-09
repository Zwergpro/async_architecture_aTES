from faststream.kafka.fastapi import KafkaMessage
from faststream.kafka.fastapi import KafkaRouter
from faststream.kafka.fastapi import Logger

from packages.schema_registry import SchemaRegistry
from packages.schema_registry.events.users.lifecycle.v1 import UserLifecycleEventType
from task_tracker.src.db import session_maker
from task_tracker.src.models import User
from task_tracker.src.repositories.user import UserRepository

BOOTSTRAP_SERVERS = 'kafka:9092'

router = KafkaRouter(BOOTSTRAP_SERVERS)


@router.subscriber('user.streaming', group_id='tracker_v1')
async def user_streaming_handler(message: KafkaMessage, logger: Logger):
    if message.headers['version'] != '1':
        logger.info('V1 incompatible version: %s', message)
        return  # skip

    data = SchemaRegistry.deserialize(message.body, 'user.streaming', version=1)

    logger.info(data)

    async with session_maker() as session:
        user: User | None = await UserRepository(session).get_user_by_public_id(data.public_id)
        if not user:
            # TODO: обработать отсутствие пользователя
            return

        user.username = data.username
        user.is_active = data.is_active
        user.role = data.role

        await session.flush([user])
        await session.commit()
        logger.info('User updated: %s', user.username)


@router.subscriber('user.lifecycle', group_id='tracker_v1')
async def user_lifecycle_handler_v1(message: KafkaMessage, logger: Logger):
    if message.headers['version'] != '1':
        logger.info('V1 incompatible version: %s', message)
        return  # skip

    data = SchemaRegistry.deserialize(message.body, 'user.lifecycle', version=1)

    logger.info(data)

    if data.type == UserLifecycleEventType.CREATED:
        async with session_maker() as session:
            user = await UserRepository(session).create_user(
                public_id=data.public_id,
                username=data.username,
                role=data.role,
            )
            logger.info('User created: %s', user.username)
