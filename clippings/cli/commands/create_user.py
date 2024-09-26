from __future__ import annotations

import argparse
import getpass

from clippings.cli.controllers import CreateUserController
from clippings.cli.core import AsyncCommand, render_result


class CreateUserCommand(AsyncCommand):
    """Create a new user"""

    @classmethod
    def setup_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("nickname", type=str, help="User nickname")

    async def run(self, args: argparse.Namespace) -> None:
        password = getpass.getpass(f"Password for {args.nickname}: ")
        controller = CreateUserController()
        result = await controller.execute(args.nickname, password)
        render_result(result)
