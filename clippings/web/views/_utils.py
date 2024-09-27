from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.responses import HTMLResponse as StarletteHTMLResponse
from starlette.responses import RedirectResponse as StarletteRedirectResponse
from starlette.responses import Response as StarletteResponse

from clippings.web.controllers.responses import HTMLResponse, RedirectResponse, Response

if TYPE_CHECKING:
    from starlette.requests import Request


def get_string_path_param(request: Request, param_name: str) -> str:
    param = request.path_params.get(param_name)
    if param is None:
        raise ValueError(f"Path parameter '{param_name}' is required")
    if not isinstance(param, str):
        raise ValueError(f"Path parameter '{param_name}' must be a string")
    return param


def convert_response(response: Response) -> StarletteResponse:
    if isinstance(response, HTMLResponse):
        return StarletteHTMLResponse(response.payload, status_code=response.status_code)
    elif isinstance(response, RedirectResponse):
        return StarletteRedirectResponse(response.url, status_code=response.status_code)
    elif isinstance(response, Response):
        return StarletteResponse(response.payload, status_code=response.status_code)

    raise ValueError(f"Unknown response type: {type(response)}")
