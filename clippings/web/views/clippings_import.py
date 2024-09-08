from starlette.requests import Request
from starlette.responses import HTMLResponse

from clippings.web.controllers.clippings_import import (
    ClippingsImportController,
    RenderClippingsImportPage,
)


async def clipping_import_page(request: Request) -> HTMLResponse:
    controller = RenderClippingsImportPage()
    result = await controller.fire()
    return HTMLResponse(result.render(), status_code=result.status)


async def clipping_upload(request: Request) -> HTMLResponse:
    form = await request.form(max_files=1, max_fields=1)
    if not form.get("file"):
        return HTMLResponse("ERROR: No file provided", status_code=200)

    controller = ClippingsImportController()
    with form["file"].file as fp:
        result = await controller.fire(fp)
    return HTMLResponse(result.render(), status_code=result.status)
