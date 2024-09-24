import pytest

from clippings.books.use_cases.edit_book import UnlinkInlineNoteUseCase
from clippings.seedwork.exceptions import DomainError


@pytest.fixture()
def make_sut(mock_book_storage):
    def _make_sut(books_storage=mock_book_storage):
        return UnlinkInlineNoteUseCase(book_storage=books_storage)

    return _make_sut


async def test_unlink_inline_note_from_clipping(make_sut, mock_book_storage, mother):
    # Arrange
    inline_note = mother.inline_note(
        id="inline-note-id", original_id="my-clipping-id", automatically_linked=True
    )
    clipping = mother.clipping(id="clipping-id", inline_notes=[inline_note])
    book = mother.book(id="book-id", clippings=[clipping])
    await mock_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute("book-id", "clipping-id", "inline-note-id")

    # Assert
    assert result is None
    updated_book = await mock_book_storage.get("book-id")
    updated_clipping = updated_book.get_clipping("clipping-id")
    assert updated_clipping.get_inline_note("inline-note-id") is None
    unlinked_note = updated_book.get_clipping("my-clipping-id")
    assert unlinked_note is not None


async def test_return_error_when_book_not_found(make_sut, mock_book_storage, mother):
    # Arrange
    inline_note = mother.inline_note(id="inline-note-id", automatically_linked=True)
    clipping = mother.clipping(id="clipping-id", inline_notes=[inline_note])
    book = mother.book(id="book-id", clippings=[clipping])
    await mock_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute("unknown-book-id", "clipping-id", "inline-note-id")

    # Assert
    assert isinstance(result, DomainError)
    assert str(result) == "Can't find book with id: unknown-book-id"


async def test_return_error_when_clipping_not_found(
    make_sut, mock_book_storage, mother
):
    # Arrange
    inline_note = mother.inline_note(id="inline-note-id", automatically_linked=True)
    clipping = mother.clipping(id="clipping-id", inline_notes=[inline_note])
    book = mother.book(id="book-id", clippings=[clipping])
    await mock_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute("book-id", "unknown-clipping-id", "inline-note-id")

    # Assert
    assert isinstance(result, DomainError)
    assert str(result) == "Clipping with id unknown-clipping-id not found"


async def test_return_error_when_inline_note_not_found(
    make_sut, mock_book_storage, mother
):
    # Arrange
    inline_note = mother.inline_note(id="inline-note-id", automatically_linked=True)
    clipping = mother.clipping(id="clipping-id", inline_notes=[inline_note])
    book = mother.book(id="book-id", clippings=[clipping])
    await mock_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute("book-id", "clipping-id", "unknown-inline-note-id")

    # Assert
    assert isinstance(result, DomainError)
    assert str(result) == "Inline note with id unknown-inline-note-id not found"


async def test_return_error_when_inline_note_is_not_autolinked(
    make_sut, mock_book_storage, mother
):
    # Arrange
    inline_note = mother.inline_note(id="inline-note-id", automatically_linked=False)
    clipping = mother.clipping(id="clipping-id", inline_notes=[inline_note])
    book = mother.book(id="book-id", clippings=[clipping])
    await mock_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute("book-id", "clipping-id", "inline-note-id")

    # Assert
    assert isinstance(result, DomainError)
    assert str(result) == "Can't restore not autolinked note"
