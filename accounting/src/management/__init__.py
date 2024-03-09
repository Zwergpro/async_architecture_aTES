import pkgutil
from importlib import import_module
from typing import Callable
from typing import NoReturn

import typer

from accounting.src.conf import settings

init_commands = typer.Typer()


def find_commands(command_dir: str) -> list[str]:
    return [
        name
        for _, name, is_pkg in pkgutil.iter_modules([command_dir])
        if not is_pkg and not name.startswith('_')
    ]


def get_commands() -> dict[str, str]:
    return {
        name: 'src'
        for name in find_commands(settings.BASE_DIR / 'accounting/src/management/commands/')
    }


def get_command_fail(exc: Exception, name: str) -> Callable[[], NoReturn]:
    def _command_fail() -> NoReturn:
        """Failed to load command"""
        raise exc

    _command_fail.__name__ = name

    return _command_fail


for command_name, base_path in get_commands().items():
    try:
        module = import_module(f'{base_path}.management.commands.{command_name}')
    except ModuleNotFoundError as exc:
        command_function = get_command_fail(exc, command_name)
    else:
        command_function = getattr(module, command_name)

    help_text = command_function.__doc__
    init_commands.command(help=help_text)(command_function)
