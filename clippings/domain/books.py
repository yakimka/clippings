from __future__ import annotations

import abc
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from datetime import datetime


@dataclass
class Book:
    id: str
    title: str
    author: Author
    clippings: list[Clipping]


@dataclass
class Author:
    id: str
    name: str


class ClippingType(Enum):
    HIGHLIGHT = "highlight"
    NOTE = "note"


@dataclass
class Clipping:
    id: str
    page: int
    location: tuple[int, int]
    type: ClippingType
    content: str
    added_at: datetime


class BooksStorage(abc.ABC):
    @abc.abstractmethod
    async def get(self, id: str) -> Book | None:
        pass

    @abc.abstractmethod
    async def add(self, book: Book) -> None:
        pass

    @abc.abstractmethod
    async def extend(self, books: list[Book]) -> None:
        pass


@dataclass(frozen=True)
class FinderQuery:
    start: int = 0
    limit: int | None = 10


_default_query = FinderQuery()


class BooksFinderABC(abc.ABC):
    @abc.abstractmethod
    async def find(self, query: FinderQuery = _default_query) -> list[Book]:
        pass

    @abc.abstractmethod
    async def count(self, query: FinderQuery = _default_query) -> int:
        pass


@dataclass
class ClippingImportCandidateDTO:
    book_title: str
    book_author: str
    page: int
    location: tuple[int, int]
    type: ClippingType
    content: str
    added_at: datetime


class ClippingsReader(abc.ABC):
    @abc.abstractmethod
    def read(self) -> AsyncGenerator[ClippingImportCandidateDTO, None]:
        pass


class ImportClippingsUseCase:
    def __init__(self, storage: BooksStorage, reader: ClippingsReader):
        self._storage = storage
        self._reader = reader

    async def execute(self) -> None:
        pass


@dataclass
class BookOnPageDTO:
    book_id: str
    cover_url: str
    title: str
    author: str
    clippings_count: int
    last_clipping_added_at: str
    rating: int
    review: str


@dataclass
class ButtonDTO:
    label: str
    url: str


@dataclass
class SelectOptionDTO:
    label: str
    value: str


@dataclass
class SelectDTO:
    label: str
    options: list[SelectOptionDTO]


@dataclass
class BooksPageDTO:
    books: list[BookOnPageDTO]
    page: int
    total_pages: int
    import_button: ButtonDTO
    add_book_button: ButtonDTO
    sort_select: SelectDTO


class BooksPresenterABC(abc.ABC):
    @abc.abstractmethod
    async def for_page(self, page: int, on_page: int) -> BooksPageDTO:
        pass


class BooksPageHtmlRenderedABC(abc.ABC):
    @abc.abstractmethod
    async def render(self, dto: BooksPageDTO) -> str:
        pass
