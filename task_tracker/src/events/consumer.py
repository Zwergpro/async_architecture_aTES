from faststream.kafka.fastapi import KafkaRouter
from faststream.kafka.fastapi import Logger

from packages.schema_registry.events.user import UserCreated
from packages.schema_registry.events.user import UserCUD
from task_tracker.src.db import session_maker
from task_tracker.src.models import User
from task_tracker.src.repositories.user import UserRepository

BOOTSTRAP_SERVERS = 'kafka:9092'

router = KafkaRouter(BOOTSTRAP_SERVERS)


@router.subscriber('user.streaming')
async def user_streaming_handler(data: UserCUD, logger: Logger):
    logger.info(data)
    async with session_maker() as session:
        user: User = await UserRepository(session).get_user_by_public_id(data.public_id)

        user.username = data.username
        user.is_active = data.is_active
        user.role = data.role

        await session.flush([user])
        await session.commit()


@router.subscriber('auth.user-created')
async def user_created_handler(data: UserCreated, logger: Logger):
    logger.info(data)
    async with session_maker() as session:
        user: User = await UserRepository(session).get_user_by_public_id(data.public_id)
        if user:
            return

        user = User(
            public_id=data.public_id,
            username=data.username,
            is_active=True,
            role=data.role,
        )
        session.add(user)
        await session.commit()
