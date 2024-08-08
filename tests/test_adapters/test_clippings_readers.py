from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clippings.adapters.clippings import MockClippingsReader

if TYPE_CHECKING:
    from clippings.domain.clippings import Clipping, ClippingsReader


@pytest.fixture()
def make_sut():
    def _make_sut(clippings: list[Clipping]) -> ClippingsReader:
        return MockClippingsReader(clippings)

    return _make_sut


async def test_can_read_from_reader(make_sut, mother):
    clippings = [mother.clipping(id=f"clipping:{i}") for i in range(3)]
    sut = make_sut(clippings)

    result = [item async for item in sut.read()]

    assert result == clippings
