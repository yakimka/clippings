from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clippings.adapters.books import (
    BooksPageHtmlRendered,
    BooksPresenter,
    MockBooksFinder,
)

if TYPE_CHECKING:
    from clippings.domain.books import BooksPageHtmlRenderedABC


@pytest.fixture()
def page_presenter(mother):
    books = [mother.book(id=f"b:{i}") for i in range(5)]
    finder = MockBooksFinder({book.id: book for book in books})
    return BooksPresenter(finder)


@pytest.fixture()
def make_sut():
    def _make_sut() -> BooksPageHtmlRenderedABC:
        return BooksPageHtmlRendered()

    return _make_sut


async def test_can_render_books_page(page_presenter, make_sut):
    sut = make_sut()
    page_data = await page_presenter.for_page(page=1, on_page=2)

    result = await sut.render(page_data)

    assert isinstance(result, str)
    assert "<!DOCTYPE html>" in result
