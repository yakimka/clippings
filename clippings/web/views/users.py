from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.responses import Response

from clippings.web.controllers.users import RenderSettingsPageController
from clippings.web.views._utils import convert_response

if TYPE_CHECKING:
    from starlette.requests import Request


async def logout(request: Request) -> Response:  # noqa: U100
    return Response(
        content="Authentication required",
        status_code=401,
        headers={
            "HX-Location": "/",
            "WWW-Authenticate": 'Basic realm="Protected Area"',
        },
    )


async def settings_page(request: Request) -> Response:  # noqa: U100
    controller = RenderSettingsPageController()
    result = await controller.fire()
    return convert_response(result)
