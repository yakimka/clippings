from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.responses import HTMLResponse

from clippings.web.presenters.book.system_pages import (
    not_found_page_presenter,
    server_error_page_presenter,
)

if TYPE_CHECKING:
    from starlette.requests import Request


async def not_found_view(
    request: Request, exc: Exception  # noqa: U100
) -> HTMLResponse:
    result = not_found_page_presenter()
    return HTMLResponse(content=result.render(), status_code=404)


async def server_error_view(
    request: Request, exc: Exception  # noqa: U100
) -> HTMLResponse:
    result = server_error_page_presenter()
    return HTMLResponse(content=result.render(), status_code=500)
