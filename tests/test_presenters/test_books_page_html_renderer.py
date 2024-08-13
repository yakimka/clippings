from __future__ import annotations

import pytest

from clippings.books.adapters.finders import MockBooksFinder
from clippings.books.presenters.books_page_presenter import (
    BooksPageHtmlRendered,
    BooksPagePresenter,
    BooksPageStringRenderedABC,
)


@pytest.fixture()
def page_presenter(mother):
    books = [mother.book(id=f"b:{i}") for i in range(5)]
    finder = MockBooksFinder({book.id: book for book in books})
    return BooksPagePresenter(finder)


@pytest.fixture()
def make_sut():
    def _make_sut() -> BooksPageStringRenderedABC:
        return BooksPageHtmlRendered()

    return _make_sut


async def test_can_render_books_page(page_presenter, make_sut):
    sut = make_sut()
    page_data = await page_presenter.present(page=1, on_page=2)

    result = await sut.render(page_data)

    assert isinstance(result, str)
    assert "<!doctype html>" in result.lower()
