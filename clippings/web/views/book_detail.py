from starlette.requests import Request
from starlette.responses import HTMLResponse

from clippings.web.controllers.book_detail import (
    RenderBookClippingDetailController,
    RenderBookClippingListController,
    RenderBookDetailPageController,
    RenderBookInfoController,
    RenderBookReviewController,
)


async def book_detail_page(request: Request) -> HTMLResponse:
    book_id = request.path_params.get("book_id")
    controller = RenderBookDetailPageController()
    result = await controller.fire(book_id)
    return HTMLResponse(result.render(), status_code=result.status)


async def book_info(request: Request) -> HTMLResponse:
    book_id = request.path_params.get("book_id")
    controller = RenderBookInfoController()
    result = await controller.fire(book_id)
    return HTMLResponse(result.render(), status_code=result.status)


async def book_review(request: Request) -> HTMLResponse:
    book_id = request.path_params.get("book_id")
    controller = RenderBookReviewController()
    result = await controller.fire(book_id)
    return HTMLResponse(result.render(), status_code=result.status)


async def clipping_list(request: Request) -> HTMLResponse:
    book_id = request.path_params.get("book_id")
    controller = RenderBookClippingListController()
    result = await controller.fire(book_id)
    return HTMLResponse(result.render(), status_code=result.status)


async def clipping_detail(request: Request) -> HTMLResponse:
    book_id = request.path_params.get("book_id")
    clipping_id = request.path_params.get("clipping_id")
    controller = RenderBookClippingDetailController()
    result = await controller.fire(book_id, clipping_id)
    return HTMLResponse(result.render(), status_code=result.status)
