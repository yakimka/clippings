import pytest

from clippings.books.use_cases.edit_book import DeleteBookUseCase
from clippings.seedwork.exceptions import CantFindEntityError


@pytest.fixture()
def make_sut(mock_book_storage, mock_deleted_hash_storage):
    def _make_sut(books_storage=mock_book_storage):
        return DeleteBookUseCase(
            book_storage=books_storage, deleted_hash_storage=mock_deleted_hash_storage
        )

    return _make_sut


async def test_remove_book(make_sut, mock_book_storage, mother):
    # Arrange
    book = mother.book(id="book-id")
    await mock_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute("book-id")

    # Assert
    assert result is None
    removed_book = await mock_book_storage.get("book-id")
    assert removed_book is None


async def test_return_error_when_book_not_found(make_sut):
    # Arrange
    sut = make_sut()

    # Act
    result = await sut.execute("unknown-book-id")

    # Assert
    assert isinstance(result, CantFindEntityError)
    assert str(result) == "Can't find book with id: unknown-book-id"
