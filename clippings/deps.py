from __future__ import annotations

from typing import TYPE_CHECKING

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from picodi import Provide, SingletonScope, dependency, inject

from clippings.books.adapters.storages import (
    MockBooksStorage,
    MockDeletedHashStorage,
    MongoBooksStorage,
    MongoDeletedHashStorage,
)
from clippings.books.use_cases.book_info import MockBookInfoClient
from clippings.settings import InfrastructureSettings
from clippings.users.adapters.password_hashers import PBKDF2PasswordHasher
from clippings.users.adapters.storages import MockUsersStorage, MongoUsersStorage

if TYPE_CHECKING:
    from clippings.books.entities import Book, DeletedHash
    from clippings.books.ports import (
        BookInfoClientABC,
        BooksStorageABC,
        DeletedHashStorageABC,
    )
    from clippings.users.entities import User
    from clippings.users.ports import PasswordHasherABC, UsersStorageABC


@dependency(scope_class=SingletonScope)
def get_infrastructure_settings() -> InfrastructureSettings:
    return InfrastructureSettings.create()


@dependency(scope_class=SingletonScope)
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
    infrastructure_settings: InfrastructureSettings = Provide(
        get_infrastructure_settings
    ),
) -> AsyncIOMotorClient:
    return AsyncIOMotorClient(infrastructure_settings.mongo.uri)


@inject
def get_mongo_database(
    mongo_client: AsyncIOMotorClient = Provide(get_mongo_client),
) -> AsyncIOMotorDatabase:
    return mongo_client.clippings_db


@dependency(scope_class=SingletonScope)
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
    mongo_books_storage: MongoBooksStorage = Provide(get_mongo_books_storage),
) -> BooksStorageABC:
    return mongo_books_storage


@dependency(scope_class=SingletonScope)
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
    mongo_deleted_hash_storage: MongoDeletedHashStorage = Provide(
        get_mongo_deleted_hash_storage
    ),
) -> DeletedHashStorageABC:
    return mongo_deleted_hash_storage


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
    mongo_users_storage: MongoUsersStorage = Provide(get_mongo_users_storage),
) -> UsersStorageABC:
    return mongo_users_storage


@inject
def get_password_hasher() -> PasswordHasherABC:
    return PBKDF2PasswordHasher()


def get_mock_book_info_client() -> MockBookInfoClient:
    return MockBookInfoClient()


@inject
def get_book_info_client(
    mock_book_info_client: MockBookInfoClient = Provide(get_mock_book_info_client),
) -> BookInfoClientABC:
    return mock_book_info_client
