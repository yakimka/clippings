from __future__ import annotations

import argparse
import importlib
import inspect
from pathlib import Path
from typing import TYPE_CHECKING

from picodi import registry

from clippings.cli import deps  # noqa: F401
from clippings.cli.core import AsyncCommand

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable


CURR_DIR = Path(__file__).parent


def collect_commands() -> Generator[tuple[str, type[AsyncCommand]], None, None]:
    for file in (CURR_DIR / "commands").glob("*.py"):
        module_name = file.stem
        if module_name == "__init__":
            continue
        module = importlib.import_module(f"clippings.cli.commands.{module_name}")
        for command_cls in module.__dict__.values():
            if (
                command_cls is not AsyncCommand
                and inspect.isclass(command_cls)
                and issubclass(command_cls, AsyncCommand)
            ):
                yield module_name, command_cls
                break


def make_parser(
    commands: Iterable[tuple[str, type[AsyncCommand]]],
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="clippings.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, cls in commands:
        sub_parser = subparsers.add_parser(name, help=cls.__doc__)
        cls.setup_parser(sub_parser)
    return parser


@registry.alifespan()
async def main() -> None:
    commands = list(collect_commands())
    parser = make_parser(commands)
    args = parser.parse_args()
    for name, cls in commands:
        if args.command == name:
            command = cls()
            await command.run(args)
            break
