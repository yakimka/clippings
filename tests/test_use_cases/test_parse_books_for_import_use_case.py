from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest

from clippings.books.adapters.readers import MockClippingsReader
from clippings.books.adapters.storages import MockBooksStorage
from clippings.books.entities import Book, ClippingType
from clippings.books.use_cases.import_clippings import (
    BookDTO,
    ClippingDTO,
    NewBookDTO,
    ParseBooksForImportUseCase,
)

if TYPE_CHECKING:
    from clippings.books.ports import BooksStorageABC, ClippingsReaderABC


@pytest.fixture()
def storage() -> BooksStorageABC:
    return MockBooksStorage()


@pytest.fixture()
def reader() -> ClippingsReaderABC:
    return MockClippingsReader([])


@pytest.fixture()
def add_existing_books(storage: MockBooksStorage):
    async def _add_existing_books(books: list[Book]):
        await storage.extend(books)

    return _add_existing_books


@pytest.fixture()
def setup_reader(reader: MockClippingsReader):
    def _setup_reader(clippings):
        reader.clippings = clippings

    return _setup_reader


@pytest.fixture()
def sut(storage, reader) -> ParseBooksForImportUseCase:
    return ParseBooksForImportUseCase(storage=storage, reader=reader)


async def test_parse_new_book_with_clippings(
    sut: ParseBooksForImportUseCase, setup_reader, mother
):
    setup_reader(
        [
            mother.clipping_import_candidate_dto(
                book_title="Book 1",
                page=1,
                location=(10, 22),
                type=ClippingType.HIGHLIGHT,
                content="The Content",
                added_at=datetime(2024, 8, 9),
            ),
        ]
    )

    result = await sut.execute()

    assert result == [
        NewBookDTO(
            title="Book 1",
            clippings=[
                ClippingDTO(
                    page=1,
                    location=(10, 22),
                    type=ClippingType.HIGHLIGHT,
                    content="The Content",
                    added_at=datetime(2024, 8, 9),
                ),
            ],
        ),
    ]


async def test_add_clippings_to_existing_book(
    sut: ParseBooksForImportUseCase, setup_reader, add_existing_books, mother
):
    await add_existing_books([mother.book(id="book:42", title="Book 1")])
    setup_reader(
        [
            mother.clipping_import_candidate_dto(
                book_title="Book 1",
                page=1,
                location=(10, 22),
                type=ClippingType.HIGHLIGHT,
                content="The Content",
                added_at=datetime(2024, 8, 9),
            ),
        ]
    )

    result = await sut.execute()

    assert result == [
        BookDTO(
            id="book:42",
            clippings=[
                ClippingDTO(
                    page=1,
                    location=(10, 22),
                    type=ClippingType.HIGHLIGHT,
                    content="The Content",
                    added_at=datetime(2024, 8, 9),
                ),
            ],
        ),
    ]
