from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from clippings.web.controllers.book_list import RenderBookListController
from clippings.web.presenters.urls import urls_manager


async def home_page(request: Request) -> RedirectResponse:
    book_list_url = urls_manager.build_url("book_list_page")
    return RedirectResponse(book_list_url.value, status_code=302)


async def book_list_page(request: Request) -> HTMLResponse:
    page = request.query_params.get("page")
    on_page = request.query_params.get("on_page")

    controller = RenderBookListController()
    result = await controller.fire(
        page=_parse_int(page, default=1), on_page=_parse_int(on_page, default=10)
    )
    return HTMLResponse(result.payload, status_code=result.status_code)


def _parse_int(value: str, *, default: int) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
