import pytest
from picodi import registry

from clippings.books.adapters.readers import MockClippingsReader
from clippings.books.adapters.storages import MockBooksStorage, MockDeletedHashStorage
from clippings.books.services import SearchBookCoverService
from clippings.books.use_cases.book_info import MockBookInfoClient
from clippings.deps import get_mongo_database_name
from clippings.settings import settings
from clippings.test.object_mother import ObjectMother
from clippings.users.adapters.password_hashers import PBKDF2PasswordHasher
from clippings.users.adapters.storages import MockUsersStorage
from clippings.users.ports import PasswordHasherABC


@pytest.fixture(scope="session", autouse=True)
def _set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(autouse=True)
def _override_deps_for_tests():
    with registry.override(get_mongo_database_name, lambda: "test_db"):
        yield


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
def search_book_cover_service(mock_book_info_client):
    return SearchBookCoverService(mock_book_info_client)
