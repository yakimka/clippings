from __future__ import annotations

from typing import TYPE_CHECKING

from clippings.books.ports import BooksStorageABC

if TYPE_CHECKING:
    from clippings.books.entities import Book


class MockBooksStorage(BooksStorageABC):
    def __init__(self) -> None:
        self._books: dict[str, Book] = {}

    async def get(self, id: str) -> Book | None:
        return self._books.get(id)

    async def add(self, book: Book) -> None:
        self._books[book.id] = book

    async def extend(self, books: list[Book]) -> None:
        for book in books:
            await self.add(book)
