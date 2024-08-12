from __future__ import annotations

from typing import TYPE_CHECKING

from clippings.books.ports import BooksFinderABC, FinderQuery

if TYPE_CHECKING:
    from clippings.books.entities import Book


_default_query = FinderQuery()


class MockBooksFinder(BooksFinderABC):
    def __init__(self, books_map: dict[str, Book] | None = None) -> None:
        self._books: dict[str, Book] = {} if books_map is None else books_map

    async def find(self, query: FinderQuery = _default_query) -> list[Book]:
        books = sorted(self._books.values(), key=lambda b: (b.title, b.id))
        start = query.start
        if query.limit is None:
            return books[start:]
        end = start + query.limit
        return books[start:end]

    async def count(self, query: FinderQuery) -> int:
        return len(await self.find(query))
