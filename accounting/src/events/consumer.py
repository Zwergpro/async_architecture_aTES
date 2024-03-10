import asyncio
import datetime

from faststream.kafka.fastapi import KafkaMessage
from faststream.kafka.fastapi import KafkaRouter
from faststream.kafka.fastapi import Logger

from accounting.src.db import session_maker
from accounting.src.models import User
from accounting.src.models.task import TaskStatus
from accounting.src.repositories.task import TaskRepository
from accounting.src.repositories.user import UserRepository
from accounting.src.services.billing import assign_task
from accounting.src.services.billing import complete_task
from packages.schema_registry import SchemaRegistry
from packages.schema_registry.events.tasks.lifecycle.v1 import TaskLifecycleEventType
from packages.schema_registry.events.users.lifecycle.v1 import UserLifecycleEventType

BOOTSTRAP_SERVERS = 'kafka:9092'

router = KafkaRouter(BOOTSTRAP_SERVERS)


@router.subscriber('user.streaming', group_id='accounting_v1')
async def user_streaming_handler(message: KafkaMessage, logger: Logger):
    if message.headers['version'] != '1':
        logger.info('V1 incompatible version: %s', message)
        return  # skip

    data = SchemaRegistry.deserialize(message.body, 'user.streaming', version=1)

    logger.info(data)
    async with session_maker() as session:
        user: User = await UserRepository(session).get_by_public_id(data.public_id)
        if not user:
            # TODO: обработать отсутствие юзера
            return

        user.username = data.username
        user.is_active = data.is_active
        user.role = data.role

        await session.flush()
        await session.commit()
        logger.info('User updated: %s', user.username)


@router.subscriber('user.lifecycle', group_id='accounting_v1')
async def user_lifecycle_handler(message: KafkaMessage, logger: Logger):
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
            await session.commit()
            logger.info('User created: %s', user.username)


@router.subscriber('task.streaming', group_id='accounting_v1')
async def task_streaming_handler(message: KafkaMessage, logger: Logger):
    if message.headers['version'] != '1':
        logger.info('V1 incompatible version: %s', message)
        return  # skip

    data = SchemaRegistry.deserialize(message.body, 'task.streaming', version=1)

    logger.info(data)
    async with session_maker() as session:
        task = await TaskRepository(session).get_by_public_id(data.public_id)
        if not task:
            task = await TaskRepository(session).create_task(
                public_id=data.public_id,
                title=data.title,
                description=data.description,
            )
            logger.info('Task created: %s', task.id)
        else:
            task.title = data.username
            task.description = data.description

            await session.flush([task])
            await session.commit()
            logger.info('Task updated: %s', task.id)


@router.subscriber('task.streaming', group_id='accounting_v2')
async def task_streaming_handler_v2(message: KafkaMessage, logger: Logger):
    if message.headers['version'] != '2':
        logger.info('V2 incompatible version: %s', message)
        return  # skip

    data = SchemaRegistry.deserialize(message.body, 'task.streaming', version=2)

    logger.info(data)
    async with session_maker() as session:
        task = await TaskRepository(session).get_by_public_id(data.public_id)
        if not task:
            task = await TaskRepository(session).create_task(
                public_id=data.public_id,
                jira_id=data.jira_id,
                title=data.title,
                description=data.description,
            )
            logger.info('V2 Task created: %s', task.id)
        else:
            task.jira_id = data.jira_id
            task.title = data.username
            task.description = data.description

            await session.flush([task])
            await session.commit()
            logger.info('V2 Task updated: %s', task.id)


@router.subscriber('task.lifecycle', group_id='accounting_v1')
async def task_lifecycle_handler(message: KafkaMessage, logger: Logger):
    if message.headers['version'] != '1':
        logger.info('V1 incompatible version: %s', message)
        return  # skip

    data = SchemaRegistry.deserialize(message.body, 'task.lifecycle', version=1)

    logger.info(data)
    # TODO: обработать случай, когда событие на создание приходит раньше чем в task.streaming
    await asyncio.sleep(2)

    if data.type == TaskLifecycleEventType.CREATED:
        async with session_maker() as session:
            task = await TaskRepository(session).get_by_public_id(data.public_id)
            task.status = TaskStatus.IN_PROGRESS
            await session.flush([task])
            await session.commit()
            logger.info('Task created: %s', task.id)

    elif data.type == TaskLifecycleEventType.ASSIGNED:
        async with session_maker() as session:
            task = await TaskRepository(session).get_by_public_id(data.public_id)
            user = await UserRepository(session).get_by_public_id(data.executor_public_id)
            await assign_task(session, task, user)
            await session.commit()
            logger.info('Task assigned: %s', task.id)

    elif data.type == TaskLifecycleEventType.COMPLETED:
        async with session_maker() as session:
            task = await TaskRepository(session).get_by_public_id(data.public_id)
            user = await UserRepository(session).get_by_public_id(data.executor_public_id)

            await complete_task(session, task, user)

            task.status = TaskStatus.DONE
            task.created_at = datetime.datetime.now()
            await session.flush([task])

            await session.commit()
            logger.info('Task completed: %s', task.id)

    else:
        logger.error('Unknown task lifecycle type: %s', data.type)
