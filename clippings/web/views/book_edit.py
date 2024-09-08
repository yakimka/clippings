from starlette.requests import Request
from starlette.responses import HTMLResponse

from clippings.web.controllers.book_edit import (
    RenderBookClippingEditFormController,
    RenderBookInfoEditFormController,
    RenderBookReviewEditFormController,
    RenderInlineNoteAddFromController,
    RenderInlineNoteEditFormController,
)


async def book_review_update_form(request: Request) -> HTMLResponse:
    book_id = request.path_params.get("book_id")
    controller = RenderBookReviewEditFormController()
    result = await controller.fire(book_id)
    return HTMLResponse(result.render(), status_code=result.status)


async def book_info_update_form(request: Request) -> HTMLResponse:
    book_id = request.path_params.get("book_id")
    controller = RenderBookInfoEditFormController()
    result = await controller.fire(book_id)
    return HTMLResponse(result.render(), status_code=result.status)


async def clipping_update_form(request: Request) -> HTMLResponse:
    book_id = request.path_params.get("book_id")
    clipping_id = request.path_params.get("clipping_id")
    controller = RenderBookClippingEditFormController()
    result = await controller.fire(book_id, clipping_id)
    return HTMLResponse(result.render(), status_code=result.status)


async def inline_note_add_form(request: Request) -> HTMLResponse:
    book_id = request.path_params.get("book_id")
    clipping_id = request.path_params.get("clipping_id")
    controller = RenderInlineNoteAddFromController()
    result = await controller.fire(book_id, clipping_id)
    return HTMLResponse(result.render(), status_code=result.status)


async def inline_note_update_form(request: Request) -> HTMLResponse:
    book_id = request.path_params.get("book_id")
    clipping_id = request.path_params.get("clipping_id")
    inline_note_id = request.path_params.get("inline_note_id")
    controller = RenderInlineNoteEditFormController()
    result = await controller.fire(book_id, clipping_id, inline_note_id)
    return HTMLResponse(result.render(), status_code=result.status)
