from __future__ import annotations

from datetime import datetime
from unittest.mock import ANY

import pytest

from clippings.books.adapters.storages import MockBooksStorage
from clippings.books.entities import Book, ClippingType
from clippings.books.presenters.book_detail.dtos import BookDetailDTO, ClippingDTO
from clippings.books.presenters.book_detail.presenters import BookDetailPresenter


@pytest.fixture()
def make_sut():
    def _make_sut(books: list[Book] | None = None) -> BookDetailPresenter:
        books_map = {book.id: book for book in books or []}
        storage = MockBooksStorage(books_map)
        return BookDetailPresenter(storage)

    return _make_sut


async def test_can_present_book_content(make_sut, mother):
    book = mother.book(
        id="book:1",
        title="The Book",
        author="The Author",
        clippings=[
            mother.clipping(
                page=(1, 2),
                location=(10, 22),
                type=ClippingType.HIGHLIGHT,
                content="some highlighted text",
                added_at=datetime(2024, 8, 9),
                inline_notes=[],
            )
        ],
    )
    sut = make_sut([book])

    result = await sut.present(book_id="book:1")

    assert result == BookDetailDTO(
        cover_url="https://placehold.co/400x600",
        title="The Book",
        author="by The Author",
        rating="Rating: 10/10",
        review="My review for this book",
        clippings=[
            ClippingDTO(
                content="some highlighted text",
                type="Highlight",
                page="Page: 1-2",
                location="Loc: 10-22",
                added_at="Added: 2024-08-09",
                inline_notes=[],
            ),
        ],
        notes_label=ANY,
        page_title=ANY,
        actions=ANY,
    )
