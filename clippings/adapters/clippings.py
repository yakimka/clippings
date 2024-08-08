from __future__ import annotations

from typing import TYPE_CHECKING

from clippings.domain.clippings import (
    Clipping,
    ClippingFilter,
    ClippingsReader,
    ClippingsStorage,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, AsyncIterator


class MockClippingsReader(ClippingsReader):
    def __init__(self, clippings: list[Clipping]) -> None:
        self._clippings = clippings

    async def read(self) -> AsyncGenerator[Clipping, None]:
        for clipping in self._clippings:
            yield clipping


class MockClippingsStorage(ClippingsStorage):
    def __init__(self) -> None:
        self._clippings: dict[str, Clipping] = {}

    async def get_many(self, filter: ClippingFilter) -> list[Clipping]:
        start = filter.start
        end = start + filter.limit
        clippings = list(self._clippings.values())
        clippings.sort(key=lambda c: (c.created_at, c.id), reverse=True)
        return clippings[start:end]

    async def add(self, clipping: Clipping) -> None:
        self._clippings[clipping.id] = clipping

    async def extend(self, clippings: AsyncIterator[Clipping]) -> None:
        async for clipping in clippings:
            await self.add(clipping)
