import pytest

from clippings.books.exceptions import CantFindEntityError
from clippings.books.use_cases.edit_book import EditInlineNoteUseCase


@pytest.fixture()
def make_sut(mock_book_storage):
    def _make_sut(books_storage=mock_book_storage):
        return EditInlineNoteUseCase(book_storage=books_storage)

    return _make_sut


async def test_update_inline_note_content(make_sut, mock_book_storage, mother):
    # Arrange
    inline_note = mother.inline_note(id="inline-note-id", content="Old content")
    clipping = mother.clipping(id="clipping-id", inline_notes=[inline_note])
    book = mother.book(id="book-id", clippings=[clipping])
    await mock_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute(
        "book-id", "clipping-id", "inline-note-id", "Updated content"
    )

    # Assert
    assert result is None
    updated_book = await mock_book_storage.get("book-id")
    updated_clipping = updated_book.get_clipping("clipping-id")
    updated_inline_note = updated_clipping.get_inline_note("inline-note-id")
    assert updated_inline_note.content == "Updated content"


async def test_return_error_when_book_not_found(make_sut):
    # Arrange
    sut = make_sut()

    # Act
    result = await sut.execute(
        "unknown-book-id", "clipping-id", "inline-note-id", "Updated content"
    )

    # Assert
    assert isinstance(result, CantFindEntityError)
    assert str(result) == "Can't find book with id: unknown-book-id"


async def test_return_error_when_clipping_not_found(
    make_sut, mock_book_storage, mother
):
    # Arrange
    book = mother.book(id="book-id", clippings=[])
    await mock_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute(
        "book-id", "unknown-clipping-id", "inline-note-id", "Updated content"
    )

    # Assert
    assert isinstance(result, CantFindEntityError)
    assert str(result) == (
        "Can't find clipping with id: unknown-clipping-id in book with id: book-id"
    )


async def test_return_error_when_inline_note_not_found(
    make_sut, mock_book_storage, mother
):
    # Arrange
    clipping = mother.clipping(id="clipping-id", inline_notes=[])
    book = mother.book(id="book-id", clippings=[clipping])
    await mock_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute(
        "book-id", "clipping-id", "unknown-inline-note-id", "Updated content"
    )

    # Assert
    assert isinstance(result, CantFindEntityError)
    assert str(result) == "Can't find inline note with id: unknown-inline-note-id"
