from __future__ import annotations

from typing import TYPE_CHECKING, Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from picodi import Provide, SingletonScope, dependency, inject
from picodi.helpers import enter

from clippings.books.adapters.storages import (
    MockBooksStorage,
    MockDeletedHashStorage,
    MongoBooksStorage,
    MongoDeletedHashStorage,
)
from clippings.books.use_cases.book_info import GoogleBookInfoClient, MockBookInfoClient
from clippings.settings import AdaptersSettings, InfrastructureSettings
from clippings.users.adapters.password_hashers import PBKDF2PasswordHasher
from clippings.users.adapters.storages import MockUsersStorage, MongoUsersStorage

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from clippings.books.entities import Book, DeletedHash
    from clippings.books.ports import (
        BookInfoClientABC,
        BooksStorageABC,
        DeletedHashStorageABC,
    )
    from clippings.users.entities import User
    from clippings.users.ports import PasswordHasherABC, UsersStorageABC


def get_default_adapters() -> AdaptersSettings:
    raise NotImplementedError("This dependency needs to be overridden")


@dependency(scope_class=SingletonScope, use_init_hook=True)
@inject
def get_infrastructure_settings(
    default_adapters: AdaptersSettings = Provide(get_default_adapters),
) -> InfrastructureSettings:
    return InfrastructureSettings.create_from_config(default_adapters)


@dependency(scope_class=SingletonScope, use_init_hook=True)
async def get_books_map() -> dict[str, dict[str, Book]]:
    return {}


def get_user_id() -> str:
    raise NotImplementedError("This dependency needs to be overridden")


@inject
def get_user_books_map(
    books_map: dict[str, dict[str, Book]] = Provide(get_books_map),
    user_id: str = Provide(get_user_id),
) -> dict[str, Book]:
    return books_map.setdefault(user_id, {})


@inject
def get_mongo_client(
    infra_settings: InfrastructureSettings = Provide(get_infrastructure_settings),
) -> AsyncIOMotorClient:
    if not infra_settings.mongo:
        raise ValueError("Mongo settings are not provided")
    return AsyncIOMotorClient(infra_settings.mongo.uri)


def get_mongo_database_name() -> str:
    return "clippings_db"


@inject
def get_mongo_database(
    mongo_client: AsyncIOMotorClient = Provide(get_mongo_client),
    database_name: str = Provide(get_mongo_database_name),
) -> AsyncIOMotorDatabase:
    return getattr(mongo_client, database_name)


@dependency(scope_class=SingletonScope, use_init_hook=True)
async def get_users_map() -> dict[str, User]:
    return {}


@inject
def get_mock_books_storage(
    books_map: dict[str, Book] = Provide(get_user_books_map),
) -> MockBooksStorage:
    return MockBooksStorage(books_map)


@inject
def get_mongo_books_storage(
    db: AsyncIOMotorDatabase = Provide(get_mongo_database),
    user_id: str = Provide(get_user_id),
) -> MongoBooksStorage:
    return MongoBooksStorage(db, user_id=user_id)


@inject
def get_books_storage(
    infra_settings: InfrastructureSettings = Provide(get_infrastructure_settings),
) -> BooksStorageABC:
    variants: dict[str, Callable[..., Any]] = {
        "mock": get_mock_books_storage,
        "mongo": get_mongo_books_storage,
    }
    with enter(variants[infra_settings.adapters.books_storage]) as storage:
        return storage


@dependency(scope_class=SingletonScope, use_init_hook=True)
async def get_deleted_hashes_map() -> dict[str, dict[str, DeletedHash]]:
    return {}


@inject
def get_user_deleted_hashes_map(
    deleted_hashes_map: dict[str, dict[str, DeletedHash]] = Provide(
        get_deleted_hashes_map
    ),
    user_id: str = Provide(get_user_id),
) -> dict[str, DeletedHash]:
    return deleted_hashes_map.setdefault(user_id, {})


@inject
def get_mock_deleted_hash_storage(
    deleted_hashes_map: dict[str, DeletedHash] = Provide(get_user_deleted_hashes_map),
) -> MockDeletedHashStorage:
    return MockDeletedHashStorage(deleted_hashes_map)


@inject
def get_mongo_deleted_hash_storage(
    db: AsyncIOMotorDatabase = Provide(get_mongo_database),
    user_id: str = Provide(get_user_id),
) -> MongoDeletedHashStorage:
    return MongoDeletedHashStorage(db, user_id)


@inject
def get_deleted_hash_storage(
    infra_settings: InfrastructureSettings = Provide(get_infrastructure_settings),
) -> DeletedHashStorageABC:
    variants: dict[str, Callable[..., Any]] = {
        "mock": get_mock_deleted_hash_storage,
        "mongo": get_mongo_deleted_hash_storage,
    }
    with enter(variants[infra_settings.adapters.deleted_hash_storage]) as storage:
        return storage


@inject
def get_mock_users_storage(
    users_map: dict = Provide(get_users_map),
) -> MockUsersStorage:
    return MockUsersStorage(users_map)


@inject
def get_mongo_users_storage(
    db: AsyncIOMotorDatabase = Provide(get_mongo_database),
) -> MongoUsersStorage:
    return MongoUsersStorage(db)


@inject
def get_users_storage(
    infra_settings: InfrastructureSettings = Provide(get_infrastructure_settings),
) -> UsersStorageABC:
    variants: dict[str, Callable[..., Any]] = {
        "mock": get_mock_users_storage,
        "mongo": get_mongo_users_storage,
    }
    with enter(variants[infra_settings.adapters.users_storage]) as storage:
        return storage


@inject
def get_password_hasher() -> PasswordHasherABC:
    return PBKDF2PasswordHasher()


def get_mock_book_info_client() -> MockBookInfoClient:
    return MockBookInfoClient()


@dependency(scope_class=SingletonScope)
@inject
async def get_google_book_info_client(
    infra_settings: InfrastructureSettings = Provide(get_infrastructure_settings),
) -> AsyncGenerator[GoogleBookInfoClient, None]:
    if not infra_settings.google_books_api:
        raise ValueError("Google Books API settings are not provided")

    client = GoogleBookInfoClient(
        timeout=infra_settings.google_books_api.timeout,
        api_key=infra_settings.google_books_api.api_key,
    )
    try:
        yield client
    finally:
        await client.aclose()


@dependency(scope_class=SingletonScope, use_init_hook=True)
@inject
async def get_book_info_client(
    infra_settings: InfrastructureSettings = Provide(get_infrastructure_settings),
) -> AsyncGenerator[BookInfoClientABC, None]:
    variants: dict[str, Callable[..., Any]] = {
        "mock": get_mock_book_info_client,
        "google": get_google_book_info_client,
    }
    async with enter(variants[infra_settings.adapters.book_info_client]) as client:
        yield client  # noqa: ASYNC119
