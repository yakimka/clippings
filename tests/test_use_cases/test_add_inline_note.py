import pytest

from clippings.books.use_cases.edit_book import AddInlineNoteUseCase
from clippings.seedwork.exceptions import DomainError


@pytest.fixture()
def make_sut(memory_book_storage):
    def _make_sut(book_storage=memory_book_storage):
        return AddInlineNoteUseCase(
            book_storage=book_storage,
            inline_note_id_generator=lambda: "inline-note-id",
        )

    return _make_sut


async def test_add_inline_note_to_clipping(make_sut, memory_book_storage, mother):
    # Arrange
    clipping = mother.clipping(id="clipping-id")
    book = mother.book(id="book-id", clippings=[clipping])
    await memory_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute("book-id", "clipping-id", "New inline note content")

    # Assert
    assert result is None
    updated_book = await memory_book_storage.get("book-id")
    updated_clipping = updated_book.get_clipping("clipping-id")
    assert len(updated_clipping.inline_notes) == 1
    updated_inline_note = updated_clipping.get_inline_note("inline-note-id")
    assert updated_inline_note.content == "New inline note content"


async def test_return_error_when_book_not_found(make_sut, memory_book_storage, mother):
    # Arrange
    clipping = mother.clipping(id="clipping-id")
    book = mother.book(id="book-id", clippings=[clipping])
    await memory_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute(
        "unknown-book-id", "clipping-id", "New inline note content"
    )

    # Assert
    assert isinstance(result, DomainError)
    assert str(result) == "Can't find book with id: unknown-book-id"


async def test_return_error_when_clipping_not_found(
    make_sut, memory_book_storage, mother
):
    # Arrange
    clipping = mother.clipping(id="clipping-id")
    book = mother.book(id="book-id", clippings=[clipping])
    await memory_book_storage.add(book)
    sut = make_sut()

    # Act
    result = await sut.execute(
        "book-id", "unknown-clipping-id", "New inline note content"
    )

    # Assert
    assert isinstance(result, DomainError)
    assert str(result) == (
        "Can't find clipping with id: unknown-clipping-id in book with id: book-id"
    )
