from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from datetime import datetime

    from clippings.books.dtos import ClippingImportCandidateDTO
    from clippings.books.entities import Book, ClippingType, Position


class BooksStorageABC(abc.ABC):
    @abc.abstractmethod
    async def get(self, id: str) -> Book | None:
        pass

    @abc.abstractmethod
    async def get_many(self, ids: list[str]) -> list[Book]:
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
    async def count(self, query: FinderQuery) -> int:
        pass


class ClippingsReaderABC(abc.ABC):
    @abc.abstractmethod
    def read(self) -> AsyncGenerator[ClippingImportCandidateDTO, None]:
        pass


class BookForGenerateId(Protocol):
    title: str
    authors: list[str]


class BookIdGenerator(Protocol):
    def __call__(self, book: BookForGenerateId) -> str:
        pass


class ClippingForGenerateId(Protocol):
    page: Position
    location: Position
    content: str
    type: ClippingType
    added_at: datetime


class ClippingIdGenerator(Protocol):
    def __call__(self, clipping: ClippingForGenerateId) -> str:
        pass


class InlineNoteIdGenerator(Protocol):
    def __call__(self) -> str:
        pass
