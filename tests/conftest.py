import pytest

from clippings.books.adapters.readers import MockClippingsReader
from clippings.books.adapters.storages import MockBooksStorage
from clippings.test.object_mother import ObjectMother
from clippings.users.adapters.password_hashers import PBKDF2PasswordHasher


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
def mock_clipping_reader() -> MockClippingsReader:
    return MockClippingsReader([])
