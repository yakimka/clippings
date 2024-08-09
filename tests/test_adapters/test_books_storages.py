from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clippings.adapters.books import MockBooksStorage

if TYPE_CHECKING:
    from clippings.domain.books import BooksStorage


@pytest.fixture()
def make_sut():
    def _make_sut() -> BooksStorage:
        return MockBooksStorage()

    return _make_sut


async def test_can_add_and_read_single_clipping_to_storage(make_sut, mother):
    clipping = mother.clipping(id="clipping:1")
    sut = make_sut()

    await sut.add(clipping)

    result = await sut.get("clipping:1")

    assert result == clipping


async def test_can_add_multiple_clippings_to_storage(make_sut, mother):
    clipping1 = mother.clipping(id="clipping:1")
    clipping2 = mother.clipping(id="clipping:2")
    sut = make_sut()
    await sut.extend([clipping1, clipping2])

    result1 = await sut.get("clipping:1")
    result2 = await sut.get("clipping:2")

    assert result1 == clipping1
    assert result2 == clipping2


async def test_clippings_unique_by_id(make_sut, mother):
    clippings = [
        mother.clipping(id="clipping:1", content="Content 1"),
        mother.clipping(id="clipping:1", content="Content 2"),
    ]
    sut = make_sut()
    await sut.extend(clippings)

    result = await sut.get("clipping:1")

    assert result is not None
    assert result in clippings
    assert result.content == "Content 2"
