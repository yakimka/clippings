from __future__ import annotations

from typing import TYPE_CHECKING

from clippings.domain.books import (
    Book,
    BooksStorage,
    ClippingImportCandidateDTO,
    ClippingsReader,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


class MockClippingsReader(ClippingsReader):
    def __init__(self, clippings: list[ClippingImportCandidateDTO]) -> None:
        self._clippings = clippings

    async def read(self) -> AsyncGenerator[ClippingImportCandidateDTO, None]:
        for clipping in self._clippings:
            yield clipping


class MockBooksStorage(BooksStorage):
    def __init__(self) -> None:
        self._books: dict[str, Book] = {}

    async def get(self, id: str) -> Book | None:
        return self._books.get(id)

    async def add(self, book: Book) -> None:
        self._books[book.id] = book

    async def extend(self, books: list[Book]) -> None:
        for book in books:
            await self.add(book)
