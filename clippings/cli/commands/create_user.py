from __future__ import annotations

import argparse
import getpass
from warnings import warn

from clippings.cli.controllers import CreateUserController
from clippings.cli.core import AsyncCommand, render_result


class CreateUserCommand(AsyncCommand):
    """Create a new user"""

    @classmethod
    def setup_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("nickname", type=str, help="User nickname")
        parser.add_argument("--password", type=str, help="User password")
        parser.add_argument("--max-books", type=int, default=None, help="Books limit")
        parser.add_argument(
            "--max-clippings-per-book",
            type=int,
            default=None,
            help="Clippings limit per book",
        )

    async def run(self, args: argparse.Namespace) -> None:
        if args.password:
            warn("Using --password is not recommended, use interactive mode instead")
        password = args.password or getpass.getpass(f"Password for {args.nickname}: ")
        controller = CreateUserController()
        result = await controller.execute(
            args.nickname,
            password,
            max_books=args.max_books,
            max_clippings_per_book=args.max_clippings_per_book,
        )
        render_result(result)
