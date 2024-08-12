from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clippings.books.adapters.finders import MockBooksFinder
from clippings.books.presenters.books_page_presenter import (
    BookOnPageDTO,
    BooksPagePresenter,
)

if TYPE_CHECKING:
    from clippings.books.entities import Book


@pytest.fixture()
def make_sut():
    def _make_sut(books: list[Book] | None = None) -> BooksPagePresenter:
        books_map = {book.id: book for book in books or []}
        finder = MockBooksFinder(books_map)
        return BooksPagePresenter(finder)

    return _make_sut


async def test_can_present_books_content(make_sut, mother):
    books = [
        mother.book(
            id="book:1",
            title="The Book",
            author=mother.author(name="The Author"),
        ),
        mother.book(
            id="book:2",
            title="Another Book",
            author=mother.author(name="Another Author"),
        ),
    ]
    sut = make_sut(books)

    result = await sut.present(page=1, on_page=10)

    assert result.books == [
        BookOnPageDTO(
            book_id="book:2",
            cover_url="https://example.com/cover.jpg",
            title="Another Book",
            author="Another Author",
            clippings_count=0,
            last_clipping_added_at="-",
            rating=10,
            review="",
        ),
        BookOnPageDTO(
            book_id="book:1",
            cover_url="https://example.com/cover.jpg",
            title="The Book",
            author="The Author",
            clippings_count=0,
            last_clipping_added_at="-",
            rating=10,
            review="",
        ),
    ]


@pytest.mark.parametrize(
    "page,on_page,books_count,expected_total_pages",
    [
        (1, 1, 12, 12),
        (12, 1, 12, 12),
        (2, 10, 101, 11),
        (2, 10, 99, 10),
        (2, 7, 60, 9),
    ],
)
async def test_pagination(
    page: int,
    on_page: int,
    books_count: int,
    expected_total_pages: int,
    make_sut,
    mother,
):
    books = [mother.book(id=f"book:{i}", title=f"Book {i}") for i in range(books_count)]
    sut = make_sut(books)

    result = await sut.present(page=page, on_page=on_page)

    assert result.books
    assert result.page == page
    assert result.total_pages == expected_total_pages
