from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from clippings.books.entities import Book, ClippingType
    from clippings.books.ports import BooksStorageABC, ClippingsReaderABC


@dataclass
class ClippingImportCandidateDTO:
    book_title: str
    book_author: str
    page: int
    location: tuple[int, int]
    type: ClippingType
    content: str
    added_at: datetime


class ReadClippingsImportCandidatesUseCase:
    def __init__(self, reader: ClippingsReaderABC):
        self._reader = reader

    async def execute(self) -> list[ClippingImportCandidateDTO]:
        return []


class ImportClippingsUseCase:
    def __init__(self, storage: BooksStorageABC):
        self._storage = storage

    async def execute(self, books: list[Book]) -> None:
        pass
