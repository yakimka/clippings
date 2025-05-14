import pytest

from clippings.books.use_cases.edit_book import ClippingFieldsDTO, EditClippingUseCase
from clippings.seedwork.exceptions import DomainError


@pytest.fixture()
def make_sut(memory_book_storage):
    def _make_sut(books_storage=memory_book_storage):
        return EditClippingUseCase(book_storage=books_storage)

    return _make_sut


async def test_update_clipping_content(make_sut, memory_book_storage, mother):
    # Arrange
    clipping = mother.clipping(id="clipping-id", content="Old content")
    book = mother.book(id="book-id", clippings=[clipping])
    await memory_book_storage.add(book)
    sut = make_sut()
    data = ClippingFieldsDTO(
        id="clipping-id", book_id="book-id", content="Updated content"
    )

    # Act
    result = await sut.execute(data)

    # Assert
    assert result is None
    updated_book = await memory_book_storage.get("book-id")
    updated_clipping = updated_book.get_clipping("clipping-id")
    assert updated_clipping.content == "Updated content"


async def test_return_error_when_book_not_found(make_sut, memory_book_storage, mother):
    # Arrange
    clipping = mother.clipping(id="clipping-id", content="Old content")
    book = mother.book(id="book-id", clippings=[clipping])
    await memory_book_storage.add(book)
    sut = make_sut()
    data = ClippingFieldsDTO(
        id="clipping-id", book_id="unknown-book-id", content="Updated content"
    )

    # Act
    result = await sut.execute(data)

    # Assert
    assert isinstance(result, DomainError)
    assert str(result) == "Can't find book with id: unknown-book-id"


async def test_return_error_when_clipping_not_found(
    make_sut, memory_book_storage, mother
):
    # Arrange
    clipping = mother.clipping(id="clipping-id", content="Old content")
    book = mother.book(id="book-id", clippings=[clipping])
    await memory_book_storage.add(book)
    sut = make_sut()
    data = ClippingFieldsDTO(
        id="unknown-clipping-id", book_id="book-id", content="Updated content"
    )

    # Act
    result = await sut.execute(data)

    # Assert
    assert isinstance(result, DomainError)
    assert "Can't find clipping with id: unknown-clipping-id" in str(result)
