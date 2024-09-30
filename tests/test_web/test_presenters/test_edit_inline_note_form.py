import pytest

from clippings.web.presenters.book.detail.forms import (
    EditInlineNoteDTO,
    EditInlineNoteFormPresenter,
)
from clippings.web.presenters.book.system_pages import NotFoundDTO
from clippings.web.presenters.urls import urls_manager


@pytest.fixture()
def make_sut(mock_book_storage):
    def _make_sut(book_storage=mock_book_storage):
        return EditInlineNoteFormPresenter(
            storage=book_storage, urls_manager=urls_manager
        )

    return _make_sut


async def test_present_should_return_edit_inline_note_dto_when_note_is_found(
    make_sut, mock_book_storage, mother
):
    sut = make_sut()
    inline_note = mother.inline_note(id="note-id", content="Sample content")
    clipping = mother.clipping(id="clipping-id", inline_notes=[inline_note])
    book = mother.book(id="book-id", clippings=[clipping])

    await mock_book_storage.add(book)

    result = await sut.present(
        book_id="book-id", clipping_id="clipping-id", inline_note_id="note-id"
    )

    assert isinstance(result.data, EditInlineNoteDTO)
    assert result.data.content == "Sample content"
    assert result.data.actions
    assert isinstance(result.render(), str)


async def test_present_should_return_not_found_when_book_is_not_found(make_sut):
    sut = make_sut()

    result = await sut.present(
        book_id="book-id", clipping_id="clipping-id", inline_note_id="note-id"
    )

    assert isinstance(result.data, NotFoundDTO)
    assert isinstance(result.render(), str)


async def test_present_should_return_not_found_when_clipping_is_not_found(
    make_sut, mock_book_storage, mother
):
    sut = make_sut()
    book = mother.book(id="book-id", clippings=[])
    await mock_book_storage.add(book)

    result = await sut.present(
        book_id="book-id", clipping_id="clipping-id", inline_note_id="note-id"
    )

    assert isinstance(result.data, NotFoundDTO)
    assert isinstance(result.render(), str)


async def test_present_should_return_not_found_when_inline_note_is_not_found(
    make_sut, mock_book_storage, mother
):
    sut = make_sut()
    clipping = mother.clipping(id="clipping-id")
    book = mother.book(id="book-id", clippings=[clipping])
    await mock_book_storage.add(book)

    result = await sut.present(
        book_id="book-id", clipping_id="clipping-id", inline_note_id="note-id"
    )

    assert isinstance(result.data, NotFoundDTO)
    assert isinstance(result.render(), str)
