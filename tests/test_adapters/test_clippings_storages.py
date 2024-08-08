from datetime import datetime
from random import shuffle  # noqa: DUO102

import pytest

from clippings.adapters.clippings import MockClippingsStorage
from clippings.domain.clippings import ClippingFilter, ClippingsStorage


@pytest.fixture()
def make_sut():
    def _make_sut() -> ClippingsStorage:
        return MockClippingsStorage()

    return _make_sut


@pytest.fixture()
def make_clippings(mother):
    def maker(count: int):
        return [mother.clipping(id=str(i)) for i in range(10, count + 1)]

    return maker


async def test_can_add_and_read_single_clipping_to_storage(make_sut, mother):
    clipping = mother.clipping()
    sut = make_sut()

    await sut.add(clipping)

    result = await sut.get_many(ClippingFilter(limit=10))

    assert result == [clipping]


async def test_can_add_and_read_multiple_clippings_to_storage(make_sut, mother):
    clippings = [mother.clipping(id=f"clipping:{i}") for i in range(3)]
    sut = make_sut()
    await sut.extend(async_iterable(clippings))

    result = await sut.get_many(ClippingFilter(limit=10))

    assert [item.id for item in result] == ["clipping:2", "clipping:1", "clipping:0"]


@pytest.mark.parametrize(
    "start,limit,expected_count,expected_start_id,expected_end_id",
    [
        pytest.param(0, 1, 1, "90", "90", id="Can request 1 item"),
        pytest.param(0, 2, 2, "90", "89", id="Can request 2 items"),
        pytest.param(10, 50, 50, "80", "31", id="Can request 50 items"),
    ],
)
async def test_can_get_fixed_number_of_clippings(
    start: int,
    limit: int,
    expected_count: int,
    expected_start_id: str,
    expected_end_id: str,
    make_sut,
    make_clippings,
):
    clippings = make_clippings(90)
    sut = make_sut()
    await sut.extend(async_iterable(clippings))

    result = await sut.get_many(ClippingFilter(start=start, limit=limit))

    assert len(result) == expected_count
    assert result[0].id == expected_start_id
    assert result[-1].id == expected_end_id


@pytest.mark.parametrize(
    "start,limit",
    [
        (0, 0),
        (1, 0),
        (10, 10),
    ],
)
async def test_can_get_zero_results(start: int, limit: int, make_sut, make_clippings):
    clippings = make_clippings(3)
    sut = make_sut()
    await sut.extend(async_iterable(clippings))

    result = await sut.get_many(ClippingFilter(start=start, limit=limit))

    assert len(result) == 0


async def test_clippings_unique_by_id(make_sut, mother):
    clippings = [
        mother.clipping(id="1"),
        mother.clipping(id="1"),
        mother.clipping(id="2"),
    ]
    sut = make_sut()
    await sut.extend(async_iterable(clippings))

    result = await sut.get_many(ClippingFilter(limit=10))
    ids = {clipping.id for clipping in result}

    assert len(result) == 2
    assert ids == {"1", "2"}


async def test_by_default_return_in_created_at_descending_order(make_sut, mother):
    clippings = [
        mother.clipping(id=str(i), created_at=datetime(2024, i, i))
        for i in range(1, 11)
    ]
    shuffled_clippings = clippings.copy()
    shuffle(shuffled_clippings)
    sut = make_sut()
    await sut.extend(async_iterable(clippings))

    result = await sut.get_many(ClippingFilter(start=0, limit=10))

    assert list(result) == list(reversed(clippings))


async def async_iterable(items):
    for item in items:
        yield item
