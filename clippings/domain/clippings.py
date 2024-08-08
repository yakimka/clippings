from __future__ import annotations

import abc
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, AsyncIterator
    from datetime import datetime


class ClippingType(Enum):
    HIGHLIGHT = "highlight"
    NOTE = "note"


@dataclass
class Clipping:
    id: str
    page: int
    location: tuple[int, int]
    type: ClippingType
    book_id: str
    content: str
    created_at: datetime


@dataclass(kw_only=True)
class ClippingFilter:
    start: int = 0
    limit: int


class ClippingsStorage(abc.ABC):
    @abc.abstractmethod
    async def get_many(self, filter: ClippingFilter) -> list[Clipping]:
        pass

    @abc.abstractmethod
    async def add(self, clipping: Clipping) -> None:
        pass

    @abc.abstractmethod
    async def extend(self, clippings: AsyncIterator[Clipping]) -> None:
        pass


class ClippingsReader(abc.ABC):
    @abc.abstractmethod
    def read(self) -> AsyncGenerator[Clipping, None]:
        pass


class ImportClippingsUseCase:
    def __init__(self, storage: ClippingsStorage, reader: ClippingsReader):
        self._storage = storage
        self._reader = reader

    async def execute(self) -> None:
        await self._storage.extend(self._reader.read())
