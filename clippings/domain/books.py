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
