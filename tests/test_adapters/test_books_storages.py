from __future__ import annotations

from random import shuffle  # noqa: DUO102
from typing import TYPE_CHECKING

import pytest

from clippings.books.adapters.storages import MockBooksStorage, MongoBooksStorage

if TYPE_CHECKING:
    from clippings.books.entities import Book
    from clippings.books.ports import BooksStorageABC


@pytest.fixture(params=["mock", "mongo"])
def make_sut(request, mongo_db):
    async def _make_sut(books: list[Book] | None = None) -> BooksStorageABC:
        if request.param == "mock":
            storage = MockBooksStorage()
        elif request.param == "mongo":
            storage = MongoBooksStorage(mongo_db, "test_user:1")
        else:
            raise ValueError(f"Unknown storage type: {request.param}")
        if books:
            await storage.extend(books)
        return storage

    return _make_sut


@pytest.fixture()
def make_books(mother):
    def maker(count: int):
        return [mother.book(id=str(i)) for i in range(10, count + 10)]

    return maker


async def test_can_add_and_read_single_book_to_storage(make_sut, mother):
    book = mother.book(id="book:1")
    sut = await make_sut()

    await sut.add(book)

    result = await sut.get("book:1")

    assert result == book


async def test_can_add_multiple_books_to_storage(make_sut, mother):
    book1 = mother.book(id="book:1")
    book2 = mother.book(id="book:2")
    sut = await make_sut()
    await sut.extend([book1, book2])

    result = await sut.get_many(["book:1", "book:2"])

    assert result == [book1, book2]


async def test_books_unique_by_id(make_sut, mother):
    books = [
        mother.book(id="book:1", title="Title 1"),
        mother.book(id="book:1", title="Title 2"),
    ]
    sut = await make_sut()
    await sut.extend(books)

    result = await sut.get("book:1")

    assert result is not None
    assert result in books
    assert result.title == "Title 2"


async def test_remove_book_from_storage(make_sut, mother):
    book = mother.book(id="book:1")
    sut = await make_sut()
    await sut.add(book)

    await sut.remove(book)

    result = await sut.get("book:1")
    assert result is None


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
    sut = await make_sut(make_books(90))

    result = await sut.find(sut.FindQuery(start=start, limit=limit))

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
    sut = await make_sut(make_books(3))

    result = await sut.find(sut.FindQuery(start=start, limit=limit))

    assert len(result) == 0


async def test_by_default_return_in_order_by_title(make_sut, mother):
    books = [mother.book(id=str(i)[::-1], title=f"Book {i}") for i in range(10, 20)]
    shuffled_books = books.copy()
    shuffle(shuffled_books)
    sut = await make_sut(books)

    result = await sut.find(sut.FindQuery(start=0, limit=None))

    assert list(result) == list(books)


async def test_can_get_count_of_books(make_sut, make_books):
    sut = await make_sut(make_books(42))

    result = await sut.count(sut.FindQuery(start=0, limit=None))

    assert result == 42
