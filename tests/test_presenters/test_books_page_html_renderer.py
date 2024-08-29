from __future__ import annotations

from unittest.mock import create_autospec

import pytest

from clippings.books.adapters.finders import MockBooksFinder
from clippings.books.presenters.book_list import (
    BooksPageHtmlRendered,
    BooksPagePresenter,
    BooksPageStringRenderedABC,
)
from clippings.books.presenters.pagination import PaginationPresenter


@pytest.fixture()
def pagination_presenter():
    presenter = create_autospec(PaginationPresenter, spec_set=True, instance=True)
    presenter.return_value = []
    return presenter


@pytest.fixture()
def page_presenter(mother, pagination_presenter):
    books = [mother.book(id=f"b:{i}") for i in range(5)]
    finder = MockBooksFinder({book.id: book for book in books})
    return BooksPagePresenter(finder, pagination_presenter=pagination_presenter)


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
