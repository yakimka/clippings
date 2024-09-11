from __future__ import annotations

from typing import TYPE_CHECKING

from picodi import Provide, SingletonScope, dependency, inject

from clippings.books.adapters.finders import MockBooksFinder
from clippings.books.adapters.storages import MockBooksStorage

if TYPE_CHECKING:
    from clippings.books.entities import Book
    from clippings.books.ports import BooksFinderABC, BooksStorageABC


@dependency(scope_class=SingletonScope)
async def get_books_map() -> dict[str, Book]:
    return {}


@inject
def get_books_storage(
    books_map: dict[str, Book] = Provide(get_books_map),
) -> BooksStorageABC:
    return MockBooksStorage(books_map)


@inject
def get_books_finder(
    books_map: dict[str, Book] = Provide(get_books_map),
) -> BooksFinderABC:
    return MockBooksFinder(books_map)
