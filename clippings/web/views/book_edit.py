from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from clippings.web.controllers.book_edit import (
    RenderBookClippingEditFormController,
    RenderBookInfoEditFormController,
    RenderBookReviewEditFormController,
    RenderInlineNoteAddFromController,
    RenderInlineNoteEditFormController,
    UpdateBookReviewController,
)


async def book_review_update_form(request: Request) -> HTMLResponse:
    book_id = request.path_params.get("book_id")
    controller = RenderBookReviewEditFormController()
    result = await controller.fire(book_id)
    return HTMLResponse(result.payload, status_code=result.status_code)


async def book_info_update_form(request: Request) -> HTMLResponse:
    book_id = request.path_params.get("book_id")
    controller = RenderBookInfoEditFormController()
    result = await controller.fire(book_id)
    return HTMLResponse(result.payload, status_code=result.status_code)


async def clipping_update_form(request: Request) -> HTMLResponse:
    book_id = request.path_params.get("book_id")
    clipping_id = request.path_params.get("clipping_id")
    controller = RenderBookClippingEditFormController()
    result = await controller.fire(book_id, clipping_id)
    return HTMLResponse(result.payload, status_code=result.status_code)


async def inline_note_add_form(request: Request) -> HTMLResponse:
    book_id = request.path_params.get("book_id")
    clipping_id = request.path_params.get("clipping_id")
    controller = RenderInlineNoteAddFromController()
    result = await controller.fire(book_id, clipping_id)
    return HTMLResponse(result.payload, status_code=result.status_code)


async def inline_note_update_form(request: Request) -> HTMLResponse:
    book_id = request.path_params.get("book_id")
    clipping_id = request.path_params.get("clipping_id")
    inline_note_id = request.path_params.get("inline_note_id")
    controller = RenderInlineNoteEditFormController()
    result = await controller.fire(book_id, clipping_id, inline_note_id)
    return HTMLResponse(result.payload, status_code=result.status_code)


async def book_review_update(request: Request) -> RedirectResponse | HTMLResponse:
    form = await request.form(max_files=1, max_fields=1)
    if "review" not in form:
        return HTMLResponse("ERROR: No review provided")
    if not isinstance(form["review"], str):
        return HTMLResponse("ERROR: Review must be a string")

    book_id = request.path_params.get("book_id")
    controller = UpdateBookReviewController()
    result = await controller.fire(book_id, form["review"] or "")
    return RedirectResponse(result.url, status_code=result.status_code)
