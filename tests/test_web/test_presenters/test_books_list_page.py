from datetime import datetime

import pytest

from clippings.web.presenters.book.list_page import BooksListPagePresenter
from clippings.web.presenters.dtos import PresenterResult
from clippings.web.presenters.pagination import classic_pagination_calculator
from clippings.web.presenters.urls import urls_manager


@pytest.fixture()
def make_sut(mock_book_storage):
    def _make_sut():
        return BooksListPagePresenter(
            storage=mock_book_storage,
            pagination_calculator=classic_pagination_calculator,
            urls_manager=urls_manager,
        )

    return _make_sut


async def test_present_books_list(make_sut, mock_book_storage, mother):
    sut = make_sut()
    await mock_book_storage.extend(
        [
            mother.book(id=f"book:{i}", title=f"Test Book {i}", rating=i)
            for i in range(10)
        ]
    )

    result = await sut.present(page=2, on_page=5)

    assert isinstance(result, PresenterResult)
    assert len(result.data.books) == 5
    assert [book.rating for book in result.data.books] == ["5", "6", "7", "8", "9"]
    assert result.data.pagination
    assert isinstance(result.render(), str)


async def test_present_clippings_on_books_list(make_sut, mock_book_storage, mother):
    sut = make_sut()
    await mock_book_storage.add(
        mother.book(clippings=[mother.clipping(added_at=datetime(2024, 8, 9))])
    )

    result = await sut.present(page=1, on_page=1)

    assert isinstance(result, PresenterResult)
    assert len(result.data.books) == 1
    book = result.data.books[0]
    assert book.clippings_count == 1
    assert book.last_clipping_added_at == "09 Aug 2024"


async def test_present_book_without_rating(make_sut, mock_book_storage, mother):
    sut = make_sut()
    await mock_book_storage.add(mother.book(rating=None))

    result = await sut.present(page=1, on_page=1)

    assert isinstance(result, PresenterResult)
    assert len(result.data.books) == 1
    book = result.data.books[0]
    assert book.rating == "-"


async def test_present_book_without_clippings(make_sut, mock_book_storage, mother):
    sut = make_sut()
    await mock_book_storage.add(mother.book(clippings=[]))

    result = await sut.present(page=1, on_page=1)

    assert isinstance(result, PresenterResult)
    assert len(result.data.books) == 1
    book = result.data.books[0]
    assert book.clippings_count == 0
    assert book.last_clipping_added_at == "-"
