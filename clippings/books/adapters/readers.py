from __future__ import annotations

from typing import TYPE_CHECKING

from clippings.books.adapters.kindle_parser.parser import KindleClippingsParser
from clippings.books.dtos import ClippingImportCandidateDTO
from clippings.books.entities import ClippingType
from clippings.books.ports import ClippingsReaderABC

if TYPE_CHECKING:
    import io
    from collections.abc import AsyncGenerator


class MockClippingsReader(ClippingsReaderABC):
    def __init__(self, clippings: list[ClippingImportCandidateDTO]) -> None:
        self.clippings = clippings

    async def read(self) -> AsyncGenerator[ClippingImportCandidateDTO, None]:
        for clipping in self.clippings:
            yield clipping


class KindleClippingsReader(ClippingsReaderABC):
    def __init__(self, file_object: io.TextIOWrapper) -> None:
        self._file_object = file_object

    async def read(self) -> AsyncGenerator[ClippingImportCandidateDTO, None]:
        parser = KindleClippingsParser()
        for line in self._file_object:
            parser.add_line(line)
            if (clipping := parser.get_clipping()) and clipping["type"] in ClippingType:
                yield ClippingImportCandidateDTO(
                    type=ClippingType(clipping["type"]),
                    book_title=clipping["title"],
                    content="\n".join(clipping["content"]).strip(),
                    page=clipping["page"],
                    location=clipping["location"],
                    added_at=clipping["added_at"],
                )
