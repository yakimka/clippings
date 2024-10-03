import pytest

from clippings.web.presenters.book.detail.page import (
    BookDetailDTO,
    BookDetailPagePresenter,
)
from clippings.web.presenters.book.system_pages import NotFoundDTO
from clippings.web.presenters.urls import urls_manager


@pytest.fixture()
def make_sut(mock_book_storage):
    def _make_sut(book_storage=mock_book_storage):
        return BookDetailPagePresenter(storage=book_storage, urls_manager=urls_manager)

    return _make_sut


async def test_present_should_return_book_detail_dto_when_book_is_found(
    make_sut, mock_book_storage, mother
):
    sut = make_sut()
    book = mother.book(id="book-id", title="Sample Book", clippings=[mother.clipping()])
    await mock_book_storage.add(book)

    result = await sut.present(book_id="book-id")

    assert isinstance(result.data, BookDetailDTO)
    assert result.data.title == "Sample Book"
    assert len(result.data.clippings) == 1
    assert isinstance(result.render(), str)


async def test_present_should_replace_none_with_text_representation(
    make_sut, mock_book_storage, mother
):
    sut = make_sut()
    book = mother.book(id="book-id", rating=None, meta=None)
    await mock_book_storage.add(book)

    result = await sut.present(book_id="book-id")

    assert isinstance(result.data, BookDetailDTO)
    assert "no rating" in result.data.rating.lower()
    assert isinstance(result.data.cover_url, str)
    assert isinstance(result.render(), str)


async def test_present_should_return_not_found_when_book_is_not_found(
    mock_book_storage, mother, make_sut
):
    sut = make_sut()
    await mock_book_storage.add(mother.book(id="book_2"))

    result = await sut.present(book_id="book_1")

    assert isinstance(result.data, NotFoundDTO)
    assert isinstance(result.render(), str)
