from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from starlette.types import ASGIApp, Receive, Scope, Send


class RedirectMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["path"].endswith("/"):
            scope["path"] = scope["path"].removesuffix("/")
            scope["raw_path"] = scope["path"].encode("utf-8")
        await self.app(scope, receive, send)
