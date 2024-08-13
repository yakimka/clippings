from __future__ import annotations

from typing import TYPE_CHECKING

from clippings.books.ports import ClippingsReaderABC

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from clippings.books.use_cases.import_clippings import ClippingImportCandidateDTO


class MockClippingsReader(ClippingsReaderABC):
    def __init__(self, clippings: list[ClippingImportCandidateDTO]) -> None:
        self._clippings = clippings

    async def read(self) -> AsyncGenerator[ClippingImportCandidateDTO, None]:
        for clipping in self._clippings:
            yield clipping
