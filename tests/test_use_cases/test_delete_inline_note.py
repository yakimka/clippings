import pytest

from clippings.books.use_cases.edit_book import DeleteInlineNoteUseCase
from clippings.seedwork.exceptions import DomainError


@pytest.fixture()
def make_sut(memory_book_storage, memory_deleted_hash_storage):
    def _make_sut(books_storage=memory_book_storage):
        return DeleteInlineNoteUseCase(
            book_storage=books_storage, deleted_hash_storage=memory_deleted_hash_storage
        )

    return _make_sut


async def test_delete_inline_note(make_sut, memory_book_storage, mother):
    # Arrange
    inline_note = mother.inline_note(id="inline-note-id", content="Old inline note")
    clipping = mother.clipping(
        id="clipping-id", content="Old content", inline_notes=[inline_note]
    )
    book = mother.book(id="book-id", clippings=[clipping])
    await memory_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute("book-id", "clipping-id", "inline-note-id")

    # Assert
    assert result is None
    updated_book = await memory_book_storage.get("book-id")
    updated_clipping = updated_book.get_clipping("clipping-id")
    assert updated_clipping.get_inline_note("inline-note-id") is None


async def test_return_error_when_book_not_found(make_sut, memory_book_storage, mother):
    # Arrange
    inline_note = mother.inline_note(id="inline-note-id", content="Old inline note")
    clipping = mother.clipping(
        id="clipping-id", content="Old content", inline_notes=[inline_note]
    )
    book = mother.book(id="book-id", clippings=[clipping])
    await memory_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute("unknown-book-id", "clipping-id", "inline-note-id")

    # Assert
    assert isinstance(result, DomainError)
    assert str(result) == "Can't find book with id: unknown-book-id"


async def test_return_error_when_clipping_not_found(
    make_sut, memory_book_storage, mother
):
    # Arrange
    inline_note = mother.inline_note(id="inline-note-id", content="Old inline note")
    clipping = mother.clipping(
        id="clipping-id", content="Old content", inline_notes=[inline_note]
    )
    book = mother.book(id="book-id", clippings=[clipping])
    await memory_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute("book-id", "unknown-clipping-id", "inline-note-id")

    # Assert
    assert isinstance(result, DomainError)
    assert str(result) == (
        "Can't find clipping with id: unknown-clipping-id in book with id: book-id"
    )
