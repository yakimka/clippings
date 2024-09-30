from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse

    from clippings.cli.controllers import Result


class AsyncCommand:
    @classmethod
    def setup_parser(cls, parser: argparse.ArgumentParser) -> None:
        pass

    async def run(self, args: argparse.Namespace) -> None:
        raise NotImplementedError


def render_result(result: Result) -> None:
    print(result.message)
    raise SystemExit(result.exit_code)
