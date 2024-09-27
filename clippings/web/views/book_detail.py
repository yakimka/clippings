from __future__ import annotations

from typing import TYPE_CHECKING

from clippings.web.auth import basic_auth
from clippings.web.controllers.book_detail import (
    RenderBookClippingDetailController,
    RenderBookClippingListController,
    RenderBookDetailPageController,
    RenderBookInfoController,
    RenderBookReviewController,
)
from clippings.web.views._utils import convert_response, get_string_path_param

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response


@basic_auth
async def book_detail_page(request: Request) -> Response:
    book_id = get_string_path_param(request, "book_id")
    controller = RenderBookDetailPageController()
    result = await controller.fire(book_id)
    return convert_response(result)


@basic_auth
async def book_info(request: Request) -> Response:
    book_id = get_string_path_param(request, "book_id")
    controller = RenderBookInfoController()
    result = await controller.fire(book_id)
    return convert_response(result)


@basic_auth
async def book_review(request: Request) -> Response:
    book_id = get_string_path_param(request, "book_id")
    controller = RenderBookReviewController()
    result = await controller.fire(book_id)
    return convert_response(result)


@basic_auth
async def clipping_list(request: Request) -> Response:
    book_id = get_string_path_param(request, "book_id")
    controller = RenderBookClippingListController()
    result = await controller.fire(book_id)
    return convert_response(result)


@basic_auth
async def clipping_detail(request: Request) -> Response:
    book_id = get_string_path_param(request, "book_id")
    clipping_id = get_string_path_param(request, "clipping_id")
    controller = RenderBookClippingDetailController()
    result = await controller.fire(book_id, clipping_id)
    return convert_response(result)
