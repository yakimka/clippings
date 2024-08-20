from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import ANY, create_autospec

import pytest

from clippings.books.adapters.finders import MockBooksFinder
from clippings.books.presenters.books_page_presenter import (
    BookOnPageDTO,
    BooksPagePresenter,
)
from clippings.books.presenters.dtos import PaginationItemDTO
from clippings.books.presenters.pagination_presenter import PaginationPresenter

if TYPE_CHECKING:
    from clippings.books.entities import Book


@pytest.fixture()
def pagination_presenter():
    presenter = create_autospec(PaginationPresenter, spec_set=True, instance=True)
    presenter.return_value = []
    return presenter


@pytest.fixture()
def make_sut(pagination_presenter):
    def _make_sut(books: list[Book] | None = None) -> BooksPagePresenter:
        books_map = {book.id: book for book in books or []}
        finder = MockBooksFinder(books_map)
        return BooksPagePresenter(finder, pagination_presenter=pagination_presenter)

    return _make_sut


async def test_can_present_books_content(make_sut, mother):
    books = [
        mother.book(
            id="book:1",
            title="The Book",
            author_name="The Author",
        ),
        mother.book(
            id="book:2",
            title="Another Book",
            author_name="Another Author",
        ),
    ]
    sut = make_sut(books)

    result = await sut.present(page=1, on_page=10)

    assert result.books == [
        BookOnPageDTO(
            cover_url="https://placehold.co/400x600",
            name="Another Book by Another Author",
            clippings_count=0,
            last_clipping_added_at="-",
            rating=10,
            review="",
            actions=ANY,
        ),
        BookOnPageDTO(
            cover_url="https://placehold.co/400x600",
            name="The Book by The Author",
            clippings_count=0,
            last_clipping_added_at="-",
            rating=10,
            review="",
            actions=ANY,
        ),
    ]


async def test_pagination(make_sut, pagination_presenter):
    pagination_presenter.return_value = [
        PaginationItemDTO(text="1", url="/books?page=1")
    ]
    sut = make_sut([])

    result = await sut.present(page=1, on_page=10)

    assert result.pagination == [PaginationItemDTO(text="1", url="/books?page=1")]
