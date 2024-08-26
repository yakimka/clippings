from __future__ import annotations

from typing import TYPE_CHECKING

from clippings.books.ports import BooksStorageABC

if TYPE_CHECKING:
    from clippings.books.entities import Book


class MockBooksStorage(BooksStorageABC):
    def __init__(self, books_map: dict[str, Book] | None = None) -> None:
        self.books: dict[str, Book] = {} if books_map is None else books_map

    async def get(self, id: str) -> Book | None:
        return self.books.get(id)

    async def get_many(self, ids: list[str]) -> list[Book]:
        books = []
        for id in ids:
            if book := self.books.get(id):
                books.append(book)
        return books

    async def add(self, book: Book) -> None:
        self.books[book.id] = book

    async def extend(self, books: list[Book]) -> None:
        for book in books:
            await self.add(book)
