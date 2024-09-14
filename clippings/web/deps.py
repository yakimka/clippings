from __future__ import annotations

from typing import TYPE_CHECKING

from picodi import Provide, SingletonScope, dependency, inject
from picodi.integrations.starlette import RequestScope

from clippings.books.adapters.finders import MockBooksFinder
from clippings.books.adapters.storages import MockBooksStorage
from clippings.users.adapters.password_hashers import BcryptPasswordHasher
from clippings.users.adapters.storages import MockUsersStorage
from clippings.users.entities import User
from clippings.users.use_cases.auth import AuthenticateUserUseCase

if TYPE_CHECKING:
    from clippings.books.entities import Book
    from clippings.books.ports import BooksFinderABC, BooksStorageABC
    from clippings.users.ports import PasswordHasherABC, UsersStorageABC


@dependency(scope_class=RequestScope)
def get_request_context() -> dict:
    return {}


@inject
def get_user_id(web_context: dict = Provide(get_request_context)) -> str:
    if user_id := web_context.get("user_id"):
        return user_id
    raise ValueError("User is not authenticated")


@dependency(scope_class=SingletonScope)
async def get_books_map() -> dict[str, dict[str, Book]]:
    return {}


@inject
def get_user_books_map(
    books_map: dict[str, dict[str, Book]] = Provide(get_books_map),
    user_id: str = Provide(get_user_id),
) -> dict[str, Book]:
    return books_map.setdefault(user_id, {})


@inject
def get_books_storage(
    books_map: dict[str, Book] = Provide(get_user_books_map),
) -> BooksStorageABC:
    return MockBooksStorage(books_map)


@inject
def get_books_finder(
    books_map: dict[str, Book] = Provide(get_user_books_map),
) -> BooksFinderABC:
    return MockBooksFinder(books_map)


@inject
def get_password_hasher() -> PasswordHasherABC:
    return BcryptPasswordHasher()


@dependency(scope_class=SingletonScope)
@inject
async def get_users_map(
    password_hasher: PasswordHasherABC = Provide(get_password_hasher),
) -> dict[str, User]:
    return {
        "1": User(id="1", nickname="test", hashed_password=password_hasher.hash("test"))
    }


@inject
def get_users_storage(users_map: dict = Provide(get_users_map)) -> UsersStorageABC:
    return MockUsersStorage(users_map)


@inject
def get_auth_use_case(
    users_storage: UsersStorageABC = Provide(get_users_storage),
    password_hasher: PasswordHasherABC = Provide(get_password_hasher),
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(
        users_storage=users_storage, password_hasher=password_hasher
    )
