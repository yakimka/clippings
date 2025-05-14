from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from picodi import Provide, inject

from clippings.deps import get_password_hasher, get_users_storage
from clippings.seedwork.exceptions import DomainError
from clippings.users.adapters.id_generators import user_id_generator
from clippings.users.use_cases.create_user import CreateUserUseCase, UserToCreateDTO

if TYPE_CHECKING:
    from clippings.users.ports import PasswordHasherABC, UsersStorageABC


@dataclass
class Result:
    message: str
    exit_code: int = 0


class CreateUserController:
    @inject
    def __init__(
        self,
        users_storage: UsersStorageABC = Provide(get_users_storage),
        password_hasher: PasswordHasherABC = Provide(get_password_hasher),
    ):
        self._users_storage = users_storage
        self._password_hasher = password_hasher

    async def execute(
        self,
        nickname: str,
        password: str,
        max_books: int | None = None,
        max_clippings_per_book: int | None = None,
    ) -> Result:
        use_case = CreateUserUseCase(
            users_storage=self._users_storage,
            user_id_generator=user_id_generator,
            password_hasher=self._password_hasher,
        )
        kwargs: dict[str, str | int] = {
            "nickname": nickname,
            "password": password,
        }
        if max_books is not None:
            kwargs["max_books"] = max_books
        if max_clippings_per_book is not None:
            kwargs["max_clippings_per_book"] = max_clippings_per_book
        user_to_create = UserToCreateDTO(**kwargs)  # type: ignore[arg-type]
        result = await use_case.execute(user_to_create)
        if isinstance(result, DomainError):
            return Result(message=str(result), exit_code=1)
        return Result(message=f"User {nickname} created with id '{result}'")
