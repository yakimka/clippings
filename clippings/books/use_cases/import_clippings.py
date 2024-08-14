from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from clippings.books.entities import Book
    from clippings.books.ports import BooksStorageABC, ClippingsReaderABC


class ReadClippingsImportCandidatesUseCase:
    def __init__(self, reader: ClippingsReaderABC):
        self._reader = reader

    async def execute(self) -> list[Book]:
        return []


class ImportClippingsUseCase:
    def __init__(self, storage: BooksStorageABC):
        self._storage = storage

    async def execute(self, books: list[Book]) -> None:
        pass
