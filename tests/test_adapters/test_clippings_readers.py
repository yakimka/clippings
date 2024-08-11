from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest

from clippings.books.adapters.readers import MockClippingsReader
from clippings.books.dtos import ClippingImportCandidateDTO
from clippings.books.entities import ClippingType

if TYPE_CHECKING:
    from clippings.books.ports import ClippingsReaderABC


@pytest.fixture()
def make_sut():
    def _make_sut(clippings: list[ClippingImportCandidateDTO]) -> ClippingsReaderABC:
        return MockClippingsReader(clippings)

    return _make_sut


@pytest.fixture()
def make_clipping_import_candidate_dto():
    def maker(
        book_title: str = "The Book",
        book_author: str = "The Author",
        page: int = 1,
        location: tuple[int, int] = (10, 22),
        type: ClippingType = ClippingType.HIGHLIGHT,
        content: str = "The Content",
        added_at: datetime = datetime(2024, 8, 9),  # noqa: B008
    ) -> ClippingImportCandidateDTO:
        return ClippingImportCandidateDTO(
            book_title=book_title,
            book_author=book_author,
            page=page,
            location=location,
            type=type,
            content=content,
            added_at=added_at,
        )

    return maker


async def test_can_read_from_reader(make_sut, make_clipping_import_candidate_dto):
    clippings = [make_clipping_import_candidate_dto() for _ in range(3)]
    sut = make_sut(clippings)

    result = [item async for item in sut.read()]

    assert result == clippings
