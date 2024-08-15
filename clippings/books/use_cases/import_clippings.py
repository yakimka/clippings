from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from datetime import datetime

    from clippings.books.entities import Book, ClippingType
    from clippings.books.ports import BooksStorageABC, ClippingsReaderABC


@dataclass
class ClippingDTO:
    page: int
    location: tuple[int, int]
    type: ClippingType
    content: str
    added_at: datetime


@dataclass
class NewBookDTO:
    title: str
    clippings: list[ClippingDTO]


@dataclass
class BookDTO:
    id: str
    add_clippings: list[ClippingDTO]


class ParseBooksForImportUseCase:
    def __init__(self, storage: BooksStorageABC, reader: ClippingsReaderABC):
        self._storage = storage
        self._reader = reader

    async def execute(self) -> list[NewBookDTO | BookDTO]:
        clippings_by_title: dict[str, list[ClippingDTO]] = {}
        async for candidate in self._reader.read():
            clipping = ClippingDTO(
                page=candidate.page,
                location=candidate.location,
                type=candidate.type,
                content=candidate.content,
                added_at=candidate.added_at,
            )
            clippings_by_title.setdefault(candidate.book_title, []).append(clipping)

        books_by_title = await self._storage.get_titles_map(list(clippings_by_title))

        result: list[NewBookDTO | BookDTO] = []
        for candidate_title, clippings in clippings_by_title.items():
            if existed_book := books_by_title.get(candidate_title):
                result.append(BookDTO(id=existed_book.id, add_clippings=clippings))
            else:
                result.append(NewBookDTO(title=candidate_title, clippings=clippings))

        return result


class ImportClippingsUseCase:
    def __init__(self, storage: BooksStorageABC):
        self._storage = storage

    async def execute(self, books: list[Book]) -> None:
        pass
