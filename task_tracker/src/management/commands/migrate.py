import typer
from alembic.command import downgrade
from alembic.command import upgrade
from alembic.config import Config

from task_tracker.src.conf import settings


def migrate(revision: str = typer.Option('head'), down: bool = typer.Option(False)) -> None:
    alembic_config = Config(settings.alembic.config)
    method = downgrade if down else upgrade
    method(alembic_config, revision)
