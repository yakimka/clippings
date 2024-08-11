from __future__ import annotations

from random import shuffle  # noqa: DUO102
from typing import TYPE_CHECKING

import pytest

from clippings.books.adapters.finders import MockBooksFinder
from clippings.books.ports import BooksFinderABC, FinderQuery

if TYPE_CHECKING:
    from clippings.books.entities import Book


@pytest.fixture()
def make_sut():
    def _make_sut(books: list[Book]) -> BooksFinderABC:
        books_map = {book.id: book for book in books}
        return MockBooksFinder(books_map)

    return _make_sut


@pytest.fixture()
def make_books(mother):
    def maker(count: int):
        return [mother.book(id=str(i)) for i in range(10, count + 10)]

    return maker


@pytest.mark.parametrize(
    "start,limit,expected_count,expected_start_id,expected_end_id",
    [
        pytest.param(0, 1, 1, "10", "10", id="Can request 1 item"),
        pytest.param(0, 2, 2, "10", "11", id="Can request 2 items"),
        pytest.param(10, 50, 50, "20", "69", id="Can request 50 items"),
    ],
)
async def test_can_get_fixed_number_of_items(
    start: int,
    limit: int,
    expected_count: int,
    expected_start_id: str,
    expected_end_id: str,
    make_sut,
    make_books,
):
    sut = make_sut(make_books(90))

    result = await sut.find(FinderQuery(start=start, limit=limit))

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
async def test_can_get_zero_results(start: int, limit: int, make_sut, make_books):
    sut = make_sut(make_books(3))

    result = await sut.find(FinderQuery(start=start, limit=limit))

    assert len(result) == 0


async def test_by_default_return_in_order_by_title(make_sut, mother):
    books = [
        mother.book(id=str(reversed(str(i))), title=f"Book {i}") for i in range(10, 20)
    ]
    shuffled_books = books.copy()
    shuffle(shuffled_books)
    sut = make_sut(books)

    result = await sut.find(FinderQuery(start=0, limit=None))

    assert list(result) == list(books)


async def test_can_get_count_of_books(make_sut, make_books):
    sut = make_sut(make_books(42))

    result = await sut.count()

    assert result == 42
