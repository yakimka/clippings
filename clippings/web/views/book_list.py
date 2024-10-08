from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.responses import RedirectResponse, Response

from clippings.web.auth import basic_auth
from clippings.web.controllers.book_list import RenderBookListController
from clippings.web.presenters.urls import urls_manager
from clippings.web.views._utils import convert_response

if TYPE_CHECKING:
    from starlette.requests import Request


async def home_page(request: Request) -> Response:  # noqa: U100
    book_list_url = urls_manager.build_url("book_list_page")
    return RedirectResponse(book_list_url.value, status_code=302)


@basic_auth
async def book_list_page(request: Request) -> Response:
    page = request.query_params.get("page")
    on_page = request.query_params.get("on_page")

    controller = RenderBookListController()
    result = await controller.fire(
        page=_parse_int(page, default=1), on_page=_parse_int(on_page, default=10)
    )
    return convert_response(result)


def _parse_int(value: str | None, *, default: int) -> int:
    if value is None:
        return default

    try:
        return int(value)
    except (ValueError, TypeError):
        return default
