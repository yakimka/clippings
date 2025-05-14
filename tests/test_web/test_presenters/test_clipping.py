import pytest

from clippings.web.presenters.book.detail.page import ClippingDTO, ClippingPresenter
from clippings.web.presenters.book.system_pages import NotFoundDTO
from clippings.web.presenters.urls import urls_manager


@pytest.fixture()
def make_sut(memory_book_storage):
    def _make_sut(book_storage=memory_book_storage):
        return ClippingPresenter(storage=book_storage, urls_manager=urls_manager)

    return _make_sut


async def test_present_should_return_clipping_dto_when_clipping_is_found(
    make_sut, memory_book_storage, mother
):
    sut = make_sut()
    book = mother.book(
        id="book-id",
        clippings=[
            mother.clipping(
                id="clipping-id",
                content="Sample Clipping",
                inline_notes=[
                    mother.inline_note(automatically_linked=False),
                    mother.inline_note(automatically_linked=True),
                ],
            )
        ],
    )
    await memory_book_storage.add(book)

    result = await sut.present(book_id="book-id", clipping_id="clipping-id")

    assert isinstance(result.data, ClippingDTO)
    assert result.data.content == "Sample Clipping"
    assert len(result.data.inline_notes) == 2
    assert isinstance(result.render(), str)


async def test_present_should_return_not_found_when_clipping_is_not_found(
    make_sut, memory_book_storage, mother
):
    sut = make_sut()
    book = mother.book(id="book-id", clippings=[mother.clipping(id="clipping-2")])
    await memory_book_storage.add(book)

    result = await sut.present(book_id="book-id", clipping_id="clipping-1")

    assert isinstance(result.data, NotFoundDTO)
    assert isinstance(result.render(), str)


async def test_present_should_return_not_found_when_book_is_not_found(make_sut):
    sut = make_sut()

    result = await sut.present(book_id="book-not-found", clipping_id="clipping-id")

    assert isinstance(result.data, NotFoundDTO)
    assert isinstance(result.render(), str)
