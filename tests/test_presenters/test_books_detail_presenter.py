from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import ANY

import pytest

from clippings.books.adapters.storages import MockBooksStorage
from clippings.books.presenters.books_detail_presenter import (
    BooksDetailDTO,
    BooksDetailPresenter,
)

if TYPE_CHECKING:
    from clippings.books.entities import Book


@pytest.fixture()
def make_sut():
    def _make_sut(books: list[Book] | None = None) -> BooksDetailPresenter:
        books_map = {book.id: book for book in books or []}
        storage = MockBooksStorage(books_map)
        return BooksDetailPresenter(storage)

    return _make_sut


async def test_can_present_book_content(make_sut, mother):
    book = mother.book(
        id="book:1",
        title="The Book",
        author_name="The Author",
        clippings=[mother.clipping(), mother.clipping()],
    )
    sut = make_sut([book])

    result = await sut.present(book_id="book:1")

    assert result == BooksDetailDTO(
        book_cover_url="https://placehold.co/400x600",
        book_title="The Book",
        book_author="The Author",
        book_rating=10,
        book_review="My review for this book",
        count_of_clippings=2,
        page_title=ANY,
        upload_cover_button=ANY,
        find_cover_button=ANY,
        edit_review_button=ANY,
    )
