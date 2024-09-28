import pytest

from clippings.books.adapters.readers import MockClippingsReader
from clippings.books.adapters.storages import MockBooksStorage, MockDeletedHashStorage
from clippings.test.object_mother import ObjectMother
from clippings.users.adapters.password_hashers import PBKDF2PasswordHasher
from clippings.users.adapters.storages import MockUsersStorage
from clippings.users.ports import PasswordHasherABC


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
