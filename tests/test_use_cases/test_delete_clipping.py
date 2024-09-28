import pytest

from clippings.books.exceptions import CantFindEntityError
from clippings.books.use_cases.edit_book import DeleteClippingUseCase
from clippings.seedwork.exceptions import DomainError


@pytest.fixture()
def make_sut(mock_book_storage, mock_deleted_hash_storage):
    def _make_sut(books_storage=mock_book_storage):
        return DeleteClippingUseCase(
            book_storage=books_storage, deleted_hash_storage=mock_deleted_hash_storage
        )

    return _make_sut


async def test_delete_clipping(make_sut, mock_book_storage, mother):
    # Arrange
    clipping = mother.clipping(id="clipping-id", content="Some content")
    book = mother.book(id="book-id", clippings=[clipping])
    await mock_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute("book-id", "clipping-id")

    # Assert
    assert result is None
    updated_book = await mock_book_storage.get("book-id")
    deleted_clipping = updated_book.get_clipping("clipping-id")
    assert deleted_clipping is None


async def test_return_error_when_book_not_found(make_sut):
    # Arrange
    sut = make_sut()

    # Act
    result = await sut.execute("unknown-book-id", "clipping-id")

    # Assert
    assert isinstance(result, CantFindEntityError)
    assert str(result) == "Can't find book with id: unknown-book-id"


async def test_return_error_when_clipping_not_found(
    make_sut, mock_book_storage, mother
):
    # Arrange
    clipping = mother.clipping(id="clipping-id", content="Some content")
    book = mother.book(id="book-id", clippings=[clipping])
    await mock_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute("book-id", "unknown-clipping-id")

    # Assert
    updated_book = await mock_book_storage.get("book-id")
    assert isinstance(result, DomainError)
    assert "Can't find clipping with id: unknown-clipping-id" in str(result)
    assert len(updated_book.clippings) == 1  # Ensure clipping was not removed
