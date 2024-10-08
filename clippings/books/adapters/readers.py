from __future__ import annotations

from typing import TYPE_CHECKING, BinaryIO

from clippings.books.adapters.kindle_parser.parser import KindleClippingsParser
from clippings.books.dtos import BookDTO, ClippingImportCandidateDTO
from clippings.books.entities import ClippingType
from clippings.books.ports import ClippingsReaderABC

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


class MockClippingsReader(ClippingsReaderABC):
    def __init__(self, clippings: list[ClippingImportCandidateDTO]) -> None:
        self.clippings = clippings

    async def read(self) -> AsyncGenerator[ClippingImportCandidateDTO, None]:
        for clipping in self.clippings:
            yield clipping


class KindleClippingsReader(ClippingsReaderABC):
    def __init__(self, file_object: BinaryIO) -> None:
        self._file_object = file_object
        self._encoding = "utf-8-sig"

    async def read(self) -> AsyncGenerator[ClippingImportCandidateDTO, None]:
        parser = KindleClippingsParser()
        for raw_line in self._file_object:
            line = raw_line.decode(self._encoding)
            parser.add_line(line)
            if clipping := parser.get_clipping():
                try:
                    clipping_type = ClippingType(clipping["type"])
                except ValueError:
                    continue

                yield ClippingImportCandidateDTO(
                    book=BookDTO(
                        title=clipping["title"],
                        authors=[
                            item.strip()
                            for item in clipping["authors"].split(";")
                            if item.strip()
                        ],
                    ),
                    type=clipping_type,
                    content="\n".join(clipping["content"]).strip(),
                    page=clipping["page"],
                    location=clipping["location"],
                    added_at=clipping["added_at"],
                )
