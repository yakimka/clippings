from __future__ import annotations

import pytest

from clippings.books.adapters.storages import MockBooksStorage
from clippings.books.presenters.book_detail.presenters import BookDetailPresenter
from clippings.books.presenters.books_detail_presenter import (
    BooksDetailHtmlRendered,
    BooksDetailStringRenderedABC,
)


@pytest.fixture()
def page_detail_presenter(mother):
    books = [mother.book(id=f"b:{i}") for i in range(5)]
    storage = MockBooksStorage({book.id: book for book in books})
    return BookDetailPresenter(storage)


@pytest.fixture()
def make_sut():
    def _make_sut() -> BooksDetailStringRenderedABC:
        return BooksDetailHtmlRendered()

    return _make_sut


async def test_can_render_book_detail_page(page_detail_presenter, make_sut):
    sut = make_sut()
    page_data = await page_detail_presenter.present(book_id="b:1")

    result = await sut.render(page_data)

    assert isinstance(result, str)
    assert "<!doctype html>" in result.lower()
