from __future__ import annotations

from typing import TYPE_CHECKING

from picodi import Provide, inject, registry
from picodi.integrations.starlette import RequestScope

from clippings.deps import (
    get_default_adapters,
    get_password_hasher,
    get_user_id,
    get_users_storage,
)
from clippings.settings import AdaptersSettings
from clippings.users.use_cases.auth import AuthenticateUserUseCase

if TYPE_CHECKING:

    from clippings.users.ports import PasswordHasherABC, UsersStorageABC


@registry.set_scope(scope_class=RequestScope)
def get_request_context() -> dict:
    return {}


@inject
def get_user_id_from_request(web_context: dict = Provide(get_request_context)) -> str:
    if user_id := web_context.get("user_id"):
        return user_id
    raise ValueError("User is not authenticated")


def get_default_adapters_for_web() -> AdaptersSettings:
    return AdaptersSettings.defaults_for_web()


@inject
def get_auth_use_case(
    users_storage: UsersStorageABC = Provide(get_users_storage),
    password_hasher: PasswordHasherABC = Provide(get_password_hasher),
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(
        users_storage=users_storage, password_hasher=password_hasher
    )


registry.override(get_user_id, get_user_id_from_request)
registry.override(get_default_adapters, get_default_adapters_for_web)
