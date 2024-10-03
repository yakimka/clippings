from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.datastructures import UploadFile
from starlette.responses import HTMLResponse, Response

from clippings.web.auth import basic_auth
from clippings.web.controllers.clippings_import import (
    ClippingsImportController,
    RenderClippingsImportPageController,
)
from clippings.web.views._utils import convert_response

if TYPE_CHECKING:
    from starlette.requests import Request


@basic_auth
async def clipping_import_page(request: Request) -> Response:  # noqa: U100
    controller = RenderClippingsImportPageController()
    result = await controller.fire()
    return convert_response(result)


@basic_auth
async def clipping_upload(request: Request) -> Response:
    form = await request.form(max_files=1, max_fields=1)
    if not form.get("file"):
        return HTMLResponse("ERROR: No file provided")
    if not isinstance(form["file"], UploadFile):
        return HTMLResponse("ERROR: Is not a file")

    controller = ClippingsImportController()
    with form["file"].file as fp:
        result = await controller.fire(fp)
    return convert_response(result)
