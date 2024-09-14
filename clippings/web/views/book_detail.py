from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.responses import HTMLResponse

from clippings.web.auth import basic_auth
from clippings.web.controllers.book_detail import (
    RenderBookClippingDetailController,
    RenderBookClippingListController,
    RenderBookDetailPageController,
    RenderBookInfoController,
    RenderBookReviewController,
)
from clippings.web.views._utils import get_string_path_param

if TYPE_CHECKING:
    from starlette.requests import Request


@basic_auth
async def book_detail_page(request: Request) -> HTMLResponse:
    book_id = get_string_path_param(request, "book_id")
    controller = RenderBookDetailPageController()
    result = await controller.fire(book_id)
    return HTMLResponse(result.payload, status_code=result.status_code)


@basic_auth
async def book_info(request: Request) -> HTMLResponse:
    book_id = get_string_path_param(request, "book_id")
    controller = RenderBookInfoController()
    result = await controller.fire(book_id)
    return HTMLResponse(result.payload, status_code=result.status_code)


@basic_auth
async def book_review(request: Request) -> HTMLResponse:
    book_id = get_string_path_param(request, "book_id")
    controller = RenderBookReviewController()
    result = await controller.fire(book_id)
    return HTMLResponse(result.payload, status_code=result.status_code)


@basic_auth
async def clipping_list(request: Request) -> HTMLResponse:
    book_id = get_string_path_param(request, "book_id")
    controller = RenderBookClippingListController()
    result = await controller.fire(book_id)
    return HTMLResponse(result.payload, status_code=result.status_code)


@basic_auth
async def clipping_detail(request: Request) -> HTMLResponse:
    book_id = get_string_path_param(request, "book_id")
    clipping_id = get_string_path_param(request, "clipping_id")
    controller = RenderBookClippingDetailController()
    result = await controller.fire(book_id, clipping_id)
    return HTMLResponse(result.payload, status_code=result.status_code)
