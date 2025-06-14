from __future__ import annotations

from typing import TYPE_CHECKING

from multipart.exceptions import MultipartParseError
from picodi import Provide, inject
from starlette.datastructures import UploadFile
from starlette.responses import HTMLResponse, Response

from clippings.web.auth import basic_auth
from clippings.web.controllers.clippings_export import ClippingsExportController
from clippings.web.controllers.clippings_import import (
    ClippingsImportController,
    RenderClippingsImportPageController,
)
from clippings.web.controllers.clippings_restore import ClippingsRestoreController
from clippings.web.deps import get_user_id_from_request
from clippings.web.views._utils import convert_response

if TYPE_CHECKING:
    from starlette.requests import Request


@basic_auth
async def clippings_import_page(request: Request) -> Response:  # noqa: U100
    controller = RenderClippingsImportPageController()
    result = await controller.fire()
    return convert_response(result)


@basic_auth
async def clippings_export(request: Request) -> Response:  # noqa: U100
    controller = ClippingsExportController()
    result = await controller.fire()
    return convert_response(result)


@basic_auth
@inject
async def clippings_restore(
    request: Request, user_id: str = Provide(get_user_id_from_request)
) -> Response:
    try:
        form = await request.form(max_files=1, max_fields=1)
    except MultipartParseError:
        return HTMLResponse("ERROR: Invalid form data")
    if not form.get("file"):
        return HTMLResponse("ERROR: No file provided")
    if not isinstance(form["file"], UploadFile):
        return HTMLResponse("ERROR: Is not a file")

    controller = ClippingsRestoreController()
    with form["file"].file as fp:
        result = await controller.fire(fp, user_id=user_id)
    return convert_response(result)


@basic_auth
@inject
async def clipping_upload(
    request: Request, user_id: str = Provide(get_user_id_from_request)
) -> Response:
    try:
        form = await request.form(max_files=1, max_fields=1)
    except MultipartParseError:
        return HTMLResponse("ERROR: Invalid form data")
    if not form.get("file"):
        return HTMLResponse("ERROR: No file provided")
    if not isinstance(form["file"], UploadFile):
        return HTMLResponse("ERROR: Is not a file")

    controller = ClippingsImportController()
    with form["file"].file as fp:
        result = await controller.fire(fp, user_id=user_id)
    return convert_response(result)
