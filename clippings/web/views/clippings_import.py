from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.datastructures import UploadFile
from starlette.responses import HTMLResponse

from clippings.web.controllers.clippings_import import (
    ClippingsImportController,
    RenderClippingsImportPage,
)

if TYPE_CHECKING:
    from starlette.requests import Request


async def clipping_import_page(request: Request) -> HTMLResponse:  # noqa: U100
    controller = RenderClippingsImportPage()
    result = await controller.fire()
    return HTMLResponse(result.payload, status_code=result.status_code)


async def clipping_upload(request: Request) -> HTMLResponse:
    form = await request.form(max_files=1, max_fields=1)
    if not form.get("file"):
        return HTMLResponse("ERROR: No file provided")
    if not isinstance(form["file"], UploadFile):
        return HTMLResponse("ERROR: Is not a file")

    controller = ClippingsImportController()
    with form["file"].file as fp:
        result = await controller.fire(fp)
    return HTMLResponse(result.payload, status_code=result.status_code)
