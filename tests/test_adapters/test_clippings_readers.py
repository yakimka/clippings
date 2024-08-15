from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clippings.books.adapters.readers import MockClippingsReader

if TYPE_CHECKING:
    from clippings.books.dtos import ClippingImportCandidateDTO
    from clippings.books.ports import ClippingsReaderABC


@pytest.fixture()
def make_sut():
    def _make_sut(clippings: list[ClippingImportCandidateDTO]) -> ClippingsReaderABC:
        return MockClippingsReader(clippings)

    return _make_sut


async def test_can_read_from_reader(make_sut, mother):
    clippings = [mother.clipping_import_candidate_dto() for _ in range(3)]
    sut = make_sut(clippings)

    result = [item async for item in sut.read()]

    assert result == clippings
