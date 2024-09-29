from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.responses import Response

if TYPE_CHECKING:
    from starlette.requests import Request


async def logout(request: Request) -> Response:  # noqa: U100
    return Response(
        content="Authentication required",
        status_code=401,
        headers={
            "HX-Location": "/",
            "WWW-Authenticate": 'Basic realm="Protected Area"',
        },
    )
