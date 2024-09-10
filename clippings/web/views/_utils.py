from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from starlette.requests import Request


def get_string_path_param(request: Request, param_name: str) -> str:
    param = request.path_params.get(param_name)
    if param is None:
        raise ValueError(f"Path parameter '{param_name}' is required")
    if not isinstance(param, str):
        raise ValueError(f"Path parameter '{param_name}' must be a string")
    return param
