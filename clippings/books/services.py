from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from clippings.books.entities import Book, BookMeta
from clippings.seedwork.exceptions import QuotaExceededError

if TYPE_CHECKING:
    from clippings.users.entities import User


try:
    from itertools import batched
except ImportError:
    from collections.abc import Iterable  # noqa: TC003

    def batched(iterable: list, n: int) -> Iterable:  # type: ignore[no-redef]
        return (iterable[i : i + n] for i in range(0, len(iterable), n))


if TYPE_CHECKING:
    from clippings.books.ports import BookInfoClientABC


class EnrichBooksMetaService:
    def __init__(self, book_info_client: BookInfoClientABC) -> None:
        self._book_info_client = book_info_client

    async def execute(self, books: list[Book]) -> None:
        for batch in batched(books, 4):
            await asyncio.gather(*[self._enrich(book) for book in batch])

    async def _enrich(self, book: Book) -> Book:
        author = book.get_first_author()
        book_info = None
        if author is not None:
            book_info = await self._book_info_client.get(book.title, author)
        if book_info is None:
            book_info = await self._book_info_client.get(book.title)

        if book_info:
            book_meta = BookMeta(
                isbns=book_info.isbns,
                cover_image_small=book_info.cover_image_small,
                cover_image_big=book_info.cover_image_big,
            )
            book.meta = book_meta
        return book


def check_book_limit(
    user: User, current_user_book_count: int, books_being_added_count: int
) -> None:
    if (current_user_book_count + books_being_added_count) > user.max_books:
        raise QuotaExceededError(
            quota_type="books",
            current_quota=user.max_books,
            trying_to_add=books_being_added_count,
            user_id=user.id,
        )


def check_clippings_per_book_limit(
    user: User,
    book_current_clipping_count: int,
    clippings_being_added_count: int,
    book_title: str | None = None,
) -> None:
    if (
        book_current_clipping_count + clippings_being_added_count
    ) > user.max_clippings_per_book:
        raise QuotaExceededError(
            quota_type="clippings",
            current_quota=user.max_clippings_per_book,
            trying_to_add=clippings_being_added_count,
            user_id=user.id,
            book_title=book_title or "",
        )
