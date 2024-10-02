from __future__ import annotations

from typing import TYPE_CHECKING

from clippings.books.entities import Book, BookMeta

if TYPE_CHECKING:
    from clippings.books.ports import BookInfoClientABC


class SearchBookCoverService:
    def __init__(self, book_info_client: BookInfoClientABC) -> None:
        self._book_info_client = book_info_client

    async def execute(self, book: Book) -> Book:
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
