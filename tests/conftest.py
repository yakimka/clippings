from uuid import uuid4

import pytest
from picodi import registry
from picodi.helpers import enter

from clippings.books.adapters.readers import MockClippingsReader
from clippings.books.adapters.storages import MockBooksStorage, MockDeletedHashStorage
from clippings.books.services import EnrichBooksMetaService
from clippings.books.use_cases.book_info import MockBookInfoClient
from clippings.deps import get_mongo_client, get_mongo_database, get_mongo_database_name
from clippings.settings import settings
from clippings.test.object_mother import ObjectMother
from clippings.users.adapters.password_hashers import PBKDF2PasswordHasher
from clippings.users.adapters.storages import MockUsersStorage
from clippings.users.ports import PasswordHasherABC

pytest_plugins = [
    "picodi.integrations._pytest",
    "picodi.integrations._pytest_asyncio",
]


@pytest.fixture(scope="session", autouse=True)
def _set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture()
def mongo_test_db_prefix():
    return "test_db_"


@pytest.fixture()
def mongo_test_db_name(mongo_test_db_prefix):
    return f"{mongo_test_db_prefix}{uuid4().hex}"


@pytest.fixture()
def picodi_overrides(mongo_test_db_name):
    return [(get_mongo_database_name, lambda: mongo_test_db_name)]


@pytest.fixture(autouse=True)
async def _drop_mongo_test_database(mongo_test_db_name):
    yield
    if get_mongo_database in registry.touched:
        async with enter(get_mongo_client) as mongo_client:
            await mongo_client.drop_database(mongo_test_db_name)


@pytest.fixture()
def mother():
    return ObjectMother(user_password_hasher=PBKDF2PasswordHasher())


@pytest.fixture()
def mock_storage_books_map():
    return {}


@pytest.fixture()
def mock_book_storage(mock_storage_books_map) -> MockBooksStorage:
    return MockBooksStorage(books_map=mock_storage_books_map)


@pytest.fixture()
def mock_deleted_hash_storage() -> MockDeletedHashStorage:
    return MockDeletedHashStorage()


@pytest.fixture()
def mock_clipping_reader() -> MockClippingsReader:
    return MockClippingsReader([])


@pytest.fixture()
def mock_users_storage():
    return MockUsersStorage()


@pytest.fixture()
def dummy_password_hasher():
    class DummyPasswordHasher(PasswordHasherABC):
        def hash(self, password: str) -> str:
            return f"{password}_hashed"

        def verify(self, password: str, hashed_password: str) -> bool:
            return self.hash(password) == hashed_password

    return DummyPasswordHasher()


@pytest.fixture()
def mock_book_info_client():
    return MockBookInfoClient()


@pytest.fixture()
def enrich_books_meta_service(mock_book_info_client):
    return EnrichBooksMetaService(mock_book_info_client)
