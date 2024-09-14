from __future__ import annotations

import asyncio
import base64
import functools
import inspect
from typing import TYPE_CHECKING, Any, ParamSpec

from picodi import Provide, inject
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
)
from starlette.requests import HTTPConnection, Request
from starlette.responses import Response

from clippings.seedwork.exceptions import DomainError
from clippings.web.deps import get_auth_use_case, get_request_context

if TYPE_CHECKING:
    from collections.abc import Callable

    from clippings.users.use_cases.auth import AuthenticateUserUseCase


class BasicAuthBackend(AuthenticationBackend):
    @inject
    async def authenticate(
        self,
        conn: HTTPConnection,
        request_context: dict = Provide(get_request_context),
        auth_use_case: AuthenticateUserUseCase = Provide(get_auth_use_case),
    ) -> tuple[AuthCredentials, SimpleUser] | None:
        if "Authorization" not in conn.headers:
            return None

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != "basic":
                return None
            decoded = base64.b64decode(credentials).decode("ascii")
        except ValueError:
            raise AuthenticationError("Invalid basic auth credentials")

        username, _, password = decoded.partition(":")
        result = await auth_use_case.execute(username, password)
        if isinstance(result, DomainError):
            return None

        request_context["user_id"] = result.id
        return AuthCredentials(["authenticated"]), SimpleUser(result.nickname)


_P = ParamSpec("_P")


def basic_auth(func: Callable[_P, Any]) -> Callable[_P, Any]:
    sig = inspect.signature(func)
    req_idx = 0
    for i, parameter in enumerate(sig.parameters.values()):
        if parameter.name == "request":
            req_idx = i
            break
    else:
        raise RuntimeError(f'No "request" argument on function "{func}"')

    @functools.wraps(func)
    def sync_wrapper(*args: _P.args, **kwargs: _P.kwargs) -> Any:
        request = kwargs.get("request", args[req_idx] if req_idx < len(args) else None)
        assert isinstance(request, Request)
        if not request.user.is_authenticated:
            return Response(
                content="Authentication required",
                status_code=401,
                headers={"WWW-Authenticate": "Basic"},
            )
        return func(*args, **kwargs)

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: _P.args, **kwargs: _P.kwargs) -> Any:
            result = sync_wrapper(*args, **kwargs)
            if isinstance(result, Response):
                return result
            return await result

        return async_wrapper

    return sync_wrapper
