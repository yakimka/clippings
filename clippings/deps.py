from __future__ import annotations

from typing import TYPE_CHECKING, Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from picodi import Provide, Registry, SingletonScope, registry

from clippings.books.adapters.storages import (
    MemoryBooksStorage,
    MemoryDeletedHashStorage,
    MongoBooksStorage,
    MongoDeletedHashStorage,
)
from clippings.books.use_cases.book_info import GoogleBookInfoClient, MockBookInfoClient
from clippings.settings import AdaptersSettings, InfrastructureSettings
from clippings.users.adapters.password_hashers import PBKDF2PasswordHasher
from clippings.users.adapters.storages import MemoryUsersStorage, MongoUsersStorage

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


@registry.set_scope(scope_class=SingletonScope, auto_init=True)
def get_infrastructure_settings(
    default_adapters: AdaptersSettings = Provide(get_default_adapters),
) -> InfrastructureSettings:
    return InfrastructureSettings.create_from_config(default_adapters)


@registry.set_scope(scope_class=SingletonScope, auto_init=True)
async def get_books_map() -> dict[str, dict[str, Book]]:
    return {}


def get_user_id() -> str:
    raise NotImplementedError("This dependency needs to be overridden")


def get_user_books_map(
    books_map: dict[str, dict[str, Book]] = Provide(get_books_map),
    user_id: str = Provide(get_user_id),
) -> dict[str, Book]:
    return books_map.setdefault(user_id, {})


def get_mongo_client(
    infra_settings: InfrastructureSettings = Provide(get_infrastructure_settings),
) -> AsyncIOMotorClient:
    if not infra_settings.mongo:
        raise ValueError("Mongo settings are not provided")
    return AsyncIOMotorClient(infra_settings.mongo.uri)


def get_mongo_database_name() -> str:
    return "clippings_db"


def get_mongo_database(
    mongo_client: AsyncIOMotorClient = Provide(get_mongo_client),
    database_name: str = Provide(get_mongo_database_name),
) -> AsyncIOMotorDatabase:
    return getattr(mongo_client, database_name)


@registry.set_scope(scope_class=SingletonScope, auto_init=True)
async def get_users_map() -> dict[str, User]:
    return {}


def get_memory_books_storage(
    books_map: dict[str, Book] = Provide(get_user_books_map),
) -> MemoryBooksStorage:
    return MemoryBooksStorage(books_map)


def get_mongo_books_storage(
    db: AsyncIOMotorDatabase = Provide(get_mongo_database),
    user_id: str = Provide(get_user_id),
) -> MongoBooksStorage:
    return MongoBooksStorage(db, user_id=user_id)


def get_books_storage(
    registry: Registry,
    infra_settings: InfrastructureSettings = Provide(get_infrastructure_settings),
) -> BooksStorageABC:
    variants: dict[str, Callable[..., Any]] = {
        "memory": get_memory_books_storage,
        "mongo": get_mongo_books_storage,
    }
    with registry.resolve(variants[infra_settings.adapters.books_storage]) as storage:
        return storage


@registry.set_scope(scope_class=SingletonScope, auto_init=True)
async def get_deleted_hashes_map() -> dict[str, dict[str, DeletedHash]]:
    return {}


def get_user_deleted_hashes_map(
    deleted_hashes_map: dict[str, dict[str, DeletedHash]] = Provide(
        get_deleted_hashes_map
    ),
    user_id: str = Provide(get_user_id),
) -> dict[str, DeletedHash]:
    return deleted_hashes_map.setdefault(user_id, {})


def get_memory_deleted_hash_storage(
    deleted_hashes_map: dict[str, DeletedHash] = Provide(get_user_deleted_hashes_map),
) -> MemoryDeletedHashStorage:
    return MemoryDeletedHashStorage(deleted_hashes_map)


def get_mongo_deleted_hash_storage(
    db: AsyncIOMotorDatabase = Provide(get_mongo_database),
    user_id: str = Provide(get_user_id),
) -> MongoDeletedHashStorage:
    return MongoDeletedHashStorage(db, user_id)


def get_deleted_hash_storage(
    registry: Registry,
    infra_settings: InfrastructureSettings = Provide(get_infrastructure_settings),
) -> DeletedHashStorageABC:
    variants: dict[str, Callable[..., Any]] = {
        "memory": get_memory_deleted_hash_storage,
        "mongo": get_mongo_deleted_hash_storage,
    }
    with registry.resolve(
        variants[infra_settings.adapters.deleted_hash_storage]
    ) as storage:
        return storage


def get_memory_users_storage(
    users_map: dict = Provide(get_users_map),
) -> MemoryUsersStorage:
    return MemoryUsersStorage(users_map)


def get_mongo_users_storage(
    db: AsyncIOMotorDatabase = Provide(get_mongo_database),
) -> MongoUsersStorage:
    return MongoUsersStorage(db)


def get_users_storage(
    registry: Registry,
    infra_settings: InfrastructureSettings = Provide(get_infrastructure_settings),
) -> UsersStorageABC:
    variants: dict[str, Callable[..., Any]] = {
        "memory": get_memory_users_storage,
        "mongo": get_mongo_users_storage,
    }
    with registry.resolve(variants[infra_settings.adapters.users_storage]) as storage:
        return storage


def get_password_hasher() -> PasswordHasherABC:
    return PBKDF2PasswordHasher()


def get_mock_book_info_client() -> MockBookInfoClient:
    return MockBookInfoClient()


@registry.set_scope(scope_class=SingletonScope)
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


@registry.set_scope(scope_class=SingletonScope, auto_init=True)
async def get_book_info_client(
    registry: Registry,
    infra_settings: InfrastructureSettings = Provide(get_infrastructure_settings),
) -> AsyncGenerator[BookInfoClientABC, None]:
    variants: dict[str, Callable[..., Any]] = {
        "mock": get_mock_book_info_client,
        "google": get_google_book_info_client,
    }
    async with registry.aresolve(
        variants[infra_settings.adapters.book_info_client]
    ) as client:
        yield client  # noqa: ASYNC119
