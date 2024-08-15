from __future__ import annotations

from typing import TYPE_CHECKING

from clippings.books.ports import BooksStorageABC

if TYPE_CHECKING:
    from clippings.books.entities import Book


class MockBooksStorage(BooksStorageABC):
    def __init__(self, books_map: dict[str, Book] | None = None) -> None:
        self._books: dict[str, Book] = {} if books_map is None else books_map

    async def get(self, id: str) -> Book | None:
        return self._books.get(id)

    async def get_titles_map(self, titles: list[str]) -> dict[str, Book]:
        return {
            book.title: book for book in self._books.values() if book.title in titles
        }

    async def add(self, book: Book) -> None:
        self._books[book.id] = book

    async def extend(self, books: list[Book]) -> None:
        for book in books:
            await self.add(book)
