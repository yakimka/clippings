from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.responses import RedirectResponse, Response

if TYPE_CHECKING:
    from starlette.requests import Request


async def login(request: Request) -> Response:
    if request.user.is_authenticated:
        next_url = request.query_params.get("next", "/")
        return RedirectResponse(next_url)

    return Response(
        content="Authentication required",
        status_code=401,
        headers={"WWW-Authenticate": 'Basic realm="Protected Area"'},
    )
