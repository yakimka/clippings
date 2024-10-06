from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.responses import RedirectResponse as StarletteRedirectResponse
from starlette.responses import Response as StarletteResponse
from starlette.responses import StreamingResponse as StarletteStreamingResponse

from clippings.web.controllers.responses import (
    RedirectResponse,
    Response,
    StreamingResponse,
)

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
    if isinstance(response, RedirectResponse):
        return StarletteRedirectResponse(
            response.url, status_code=response.status_code, headers=response.headers
        )
    elif isinstance(response, StreamingResponse):
        return StarletteStreamingResponse(
            response.payload,
            status_code=response.status_code,
            media_type=response.media_type,
            headers=response.headers,
        )
    elif isinstance(response, Response):
        return StarletteResponse(
            response.payload,
            status_code=response.status_code,
            media_type=response.media_type,
            headers=response.headers,
        )

    raise ValueError(f"Unknown response type: {type(response)}")
