from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.datastructures import UploadFile
from starlette.responses import HTMLResponse, Response

from clippings.web.auth import basic_auth
from clippings.web.controllers.book_edit import (
    AddInlineNoteController,
    DeleteBookController,
    DeleteClippingController,
    DeleteInlineNoteController,
    EditInlineNoteController,
    RenderBookClippingEditFormController,
    RenderBookInfoEditFormController,
    RenderBookReviewEditFormController,
    RenderInlineNoteAddFromController,
    RenderInlineNoteEditFormController,
    UnlinkInlineNoteController,
    UpdateBookInfoController,
    UpdateBookReviewController,
    UpdateClippingController,
)
from clippings.web.views._utils import convert_response, get_string_path_param

if TYPE_CHECKING:
    from starlette.requests import Request


@basic_auth
async def book_review_update_form(request: Request) -> Response:
    book_id = get_string_path_param(request, "book_id")
    controller = RenderBookReviewEditFormController()
    result = await controller.fire(book_id)
    return convert_response(result)


@basic_auth
async def book_info_update_form(request: Request) -> Response:
    book_id = get_string_path_param(request, "book_id")
    controller = RenderBookInfoEditFormController()
    result = await controller.fire(book_id)
    return convert_response(result)


@basic_auth
async def clipping_update_form(request: Request) -> Response:
    book_id = get_string_path_param(request, "book_id")
    clipping_id = get_string_path_param(request, "clipping_id")
    controller = RenderBookClippingEditFormController()
    result = await controller.fire(book_id, clipping_id)
    return convert_response(result)


@basic_auth
async def inline_note_add_form(request: Request) -> Response:
    book_id = get_string_path_param(request, "book_id")
    clipping_id = get_string_path_param(request, "clipping_id")
    controller = RenderInlineNoteAddFromController()
    result = await controller.fire(book_id, clipping_id)
    return convert_response(result)


@basic_auth
async def inline_note_update_form(request: Request) -> Response:
    book_id = get_string_path_param(request, "book_id")
    clipping_id = get_string_path_param(request, "clipping_id")
    inline_note_id = get_string_path_param(request, "inline_note_id")
    controller = RenderInlineNoteEditFormController()
    result = await controller.fire(book_id, clipping_id, inline_note_id)
    return convert_response(result)


@basic_auth
async def book_review_update(request: Request) -> Response:
    form = await request.form(max_files=10, max_fields=10)
    if "review" not in form:
        return HTMLResponse("ERROR: No review provided")
    if not isinstance(form["review"], str):
        return HTMLResponse("ERROR: Review must be a string")

    book_id = get_string_path_param(request, "book_id")
    controller = UpdateBookReviewController()
    result = await controller.fire(book_id, form["review"] or "")
    return convert_response(result)


@basic_auth
async def book_info_update(request: Request) -> Response:
    form = await request.form(max_files=10, max_fields=10)
    for field in ["title", "authors"]:
        if not form.get(field):
            return HTMLResponse(f"ERROR: No {field} provided")
    if not isinstance(form["title"], str):
        return HTMLResponse("ERROR: Title must be a string")
    if not isinstance(form["authors"], str):
        return HTMLResponse("ERROR: Authors must be a string")
    rating_raw = form.get("rating") or None
    if isinstance(rating_raw, UploadFile):
        return HTMLResponse("ERROR: Rating must be an integer")

    rating: int | None = None
    if rating_raw is not None:
        try:
            rating = int(rating_raw)
        except ValueError:
            return HTMLResponse("ERROR: Rating must be an integer")

    controller = UpdateBookInfoController()
    result = await controller.fire(
        get_string_path_param(request, "book_id"),
        title=form["title"],
        authors=form["authors"],
        rating=rating,
    )

    return convert_response(result)


@basic_auth
async def clipping_update(request: Request) -> Response:
    form = await request.form(max_files=10, max_fields=10)
    if form.get("content") is None:
        return HTMLResponse("ERROR: No content provided")

    if not isinstance(form["content"], str):
        return HTMLResponse("ERROR: Content must be a string")

    controller = UpdateClippingController()
    result = await controller.fire(
        book_id=get_string_path_param(request, "book_id"),
        clipping_id=get_string_path_param(request, "clipping_id"),
        content=form["content"],
    )

    return convert_response(result)


@basic_auth
async def inline_note_add(request: Request) -> Response:
    form = await request.form(max_files=10, max_fields=10)
    if form.get("content") is None:
        return HTMLResponse("ERROR: No content provided")

    if not isinstance(form["content"], str):
        return HTMLResponse("ERROR: Content must be a string")

    controller = AddInlineNoteController()
    result = await controller.fire(
        book_id=get_string_path_param(request, "book_id"),
        clipping_id=get_string_path_param(request, "clipping_id"),
        content=form["content"],
    )

    return convert_response(result)


@basic_auth
async def inline_note_update(request: Request) -> Response:
    form = await request.form(max_files=10, max_fields=10)
    if form.get("content") is None:
        return HTMLResponse("ERROR: No content provided")

    if not isinstance(form["content"], str):
        return HTMLResponse("ERROR: Content must be a string")

    controller = EditInlineNoteController()
    result = await controller.fire(
        book_id=get_string_path_param(request, "book_id"),
        clipping_id=get_string_path_param(request, "clipping_id"),
        inline_note_id=get_string_path_param(request, "inline_note_id"),
        content=form["content"],
    )

    return convert_response(result)


@basic_auth
async def inline_note_unlink(request: Request) -> Response:
    controller = UnlinkInlineNoteController()
    result = await controller.fire(
        book_id=get_string_path_param(request, "book_id"),
        clipping_id=get_string_path_param(request, "clipping_id"),
        inline_note_id=get_string_path_param(request, "inline_note_id"),
    )
    return convert_response(result)


@basic_auth
async def book_delete(request: Request) -> Response:
    controller = DeleteBookController()
    result = await controller.fire(book_id=get_string_path_param(request, "book_id"))
    return convert_response(result)


@basic_auth
async def clipping_delete(request: Request) -> Response:
    controller = DeleteClippingController()
    result = await controller.fire(
        book_id=get_string_path_param(request, "book_id"),
        clipping_id=get_string_path_param(request, "clipping_id"),
    )
    return convert_response(result)


@basic_auth
async def inline_note_delete(request: Request) -> Response:
    controller = DeleteInlineNoteController()
    result = await controller.fire(
        book_id=get_string_path_param(request, "book_id"),
        clipping_id=get_string_path_param(request, "clipping_id"),
        inline_note_id=get_string_path_param(request, "inline_note_id"),
    )
    return convert_response(result)
