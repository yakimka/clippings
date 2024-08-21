from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import ANY, create_autospec

import pytest

from clippings.books.adapters.storages import MockBooksStorage
from clippings.books.entities import ClippingType
from clippings.books.use_cases.import_clippings import (
    BookDTO,
    ClippingDTO,
    ImportClippingsUseCase,
    NewBookDTO,
)

if TYPE_CHECKING:
    from clippings.books.ports import BooksStorageABC


@pytest.fixture()
def storage() -> BooksStorageABC:
    storage = create_autospec(MockBooksStorage, spec_set=True, instance=True)
    storage.get.return_value = None
    storage.get_many.return_value = []
    return storage


@pytest.fixture()
def sut(storage) -> ImportClippingsUseCase:
    return ImportClippingsUseCase(storage=storage)


@pytest.fixture()
def make_new_book_dto():
    def _make_new_book_dto(
        title: str = "Book 1", clippings: list[ClippingDTO] | None = None
    ):
        return NewBookDTO(title=title, clippings=clippings or [])

    return _make_new_book_dto


@pytest.fixture()
def make_clipping_dto():
    def _make_clipping_dto(
        page: tuple[int, int] = (1, 1),
        location: tuple[int, int] = (10, 22),
        type: ClippingType = ClippingType.HIGHLIGHT,
        content: str = "some highlighted text",
        added_at: datetime = datetime(2024, 8, 9),  # noqa: B008
    ):
        return ClippingDTO(
            page=page,
            location=location,
            type=type,
            content=content,
            added_at=added_at,
        )

    return _make_clipping_dto


@pytest.fixture()
def make_book_dto():
    def _make_book_dto(id: str = "book:1", clippings: list[ClippingDTO] | None = None):
        return BookDTO(id=id, clippings=clippings or [])

    return _make_book_dto


async def test_import_new_book(
    sut, storage, make_new_book_dto, make_clipping_dto, mother
):
    book = make_new_book_dto(
        title="Book 1",
        clippings=[
            make_clipping_dto(
                page=1,
                location=(10, 22),
                type=ClippingType.HIGHLIGHT,
                content="The Content",
                added_at=datetime(2024, 8, 9),
            ),
        ],
    )

    await sut.execute(books=[book])

    storage.extend.assert_called_once_with(
        [
            mother.book(
                id=ANY,
                title="Book 1",
                author_name=None,
                clippings=[
                    mother.clipping(
                        id=ANY,
                        page=1,
                        location=(10, 22),
                        type=ClippingType.HIGHLIGHT,
                        content="The Content",
                        added_at=datetime(2024, 8, 9),
                    ),
                ],
            ),
        ]
    )


async def test_import_existed_book(
    sut, storage, make_book_dto, make_clipping_dto, mother
):
    storage.get_many.return_value = [
        mother.book(
            id="book:42",
            title="Book 1",
            author_name="The Author",
            clippings=[
                mother.clipping(
                    id="clipping:42",
                    page=(1, 1),
                    location=(10, 22),
                    type=ClippingType.HIGHLIGHT,
                    content="The Content 1",
                    added_at=datetime(2024, 8, 9),
                ),
            ],
        )
    ]

    book = make_book_dto(
        id="book:42",
        clippings=[make_clipping_dto(content="The Content 2")],
    )

    await sut.execute(books=[book])

    storage.extend.assert_called_once_with(
        [
            mother.book(
                id=ANY,
                title="Book 1",
                author_name="The Author",
                clippings=[
                    mother.clipping(
                        id="clipping:42",
                        page=(1, 1),
                        location=(10, 22),
                        type=ClippingType.HIGHLIGHT,
                        content="The Content 1",
                        added_at=datetime(2024, 8, 9),
                    ),
                    mother.clipping(id=ANY, content="The Content 2"),
                ],
            ),
        ]
    )
