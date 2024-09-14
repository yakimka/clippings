from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from picodi import Provide, inject
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
)

from clippings.seedwork.exceptions import DomainError
from clippings.web.deps import get_auth_use_case, get_request_context

if TYPE_CHECKING:
    from starlette.requests import HTTPConnection

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
