from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import ANY

import pytest

from clippings.books.adapters.id_generators import (
    clipping_id_generator,
    inline_note_id_generator,
)
from clippings.books.entities import Book, BookMeta, Clipping, ClippingType
from clippings.books.use_cases.import_clippings import (
    ImportClippingsUseCase,
    ImportedBookDTO,
)

if TYPE_CHECKING:
    from clippings.books.ports import BookIdGenerator


pytestmark = pytest.mark.usefixtures("user")


@pytest.fixture()
def autoincrement_id_generator() -> BookIdGenerator:
    ids = (str(i) for i in range(1, 1000))
    return lambda _: str(next(ids))


@pytest.fixture()
def sut(
    mock_book_storage,
    mock_clipping_reader,
    autoincrement_id_generator,
    mock_deleted_hash_storage,
    enrich_books_meta_service,
    mock_users_storage,
) -> ImportClippingsUseCase:
    return ImportClippingsUseCase(
        storage=mock_book_storage,
        reader=mock_clipping_reader,
        deleted_hash_storage=mock_deleted_hash_storage,
        enrich_books_meta_service=enrich_books_meta_service,
        book_id_generator=autoincrement_id_generator,
        clipping_id_generator=clipping_id_generator,
        inline_note_id_generator=inline_note_id_generator,
        users_storage=mock_users_storage,
    )


async def test_import_single_clipping(
    sut, mother, mock_clipping_reader, mock_book_storage
):
    # Arrange
    mock_clipping_reader.clippings = [
        mother.clipping_import_candidate_dto(
            book_title="The Book",
            book_authors=["The Author"],
            page=(1, 1),
            location=(10, 22),
            type=ClippingType.HIGHLIGHT,
            content="The Content",
            added_at=datetime(2024, 8, 9),
        )
    ]

    # Act
    await sut.execute(user_id="user:42")

    # Assert
    book = await mock_book_storage.get("1")

    assert book == Book(
        id="1",
        title="The Book",
        authors=["The Author"],
        meta=BookMeta(
            isbns=ANY,
            cover_image_small=ANY,
            cover_image_big=ANY,
        ),
        clippings=[
            Clipping(
                id="3AVVHZIWHWFGZ",
                page=(1, 1),
                location=(10, 22),
                type=ClippingType.HIGHLIGHT,
                content="The Content",
                inline_notes=[],
                added_at=datetime(2024, 8, 9),
            )
        ],
        review="",
        rating=None,
    )


async def test_use_unknown_author_if_authors_is_empty(
    sut, mother, mock_clipping_reader, mock_book_storage
):
    mock_clipping_reader.clippings = [
        mother.clipping_import_candidate_dto(book_authors="")
    ]

    await sut.execute(user_id="user:42")

    book = await mock_book_storage.get("1")
    assert book.authors == ["Unknown Author"]


async def test_import_multiple_clippings_to_new_books(
    sut, mother, mock_clipping_reader, mock_book_storage
):
    # Arrange
    mock_clipping_reader.clippings = [
        mother.clipping_import_candidate_dto(
            book_title="Book One",
            book_authors=["Author One"],
            page=(1, 1),
            location=(10, 20),
            type=ClippingType.HIGHLIGHT,
            content="Highlight from Book One",
            added_at=datetime(2024, 8, 10),
        ),
        mother.clipping_import_candidate_dto(
            book_title="Book Two",
            book_authors=["Author Two"],
            page=(2, 3),
            location=(30, 40),
            type=ClippingType.NOTE,
            content="Note from Book Two",
            added_at=datetime(2024, 8, 11),
        ),
    ]

    # Act
    result = await sut.execute(user_id="user:42")

    # Assert
    book_one = await mock_book_storage.get("1")
    book_two = await mock_book_storage.get("2")

    assert book_one.title == "Book One"
    assert len(book_one.clippings) == 1
    assert book_one.clippings[0].content == "Highlight from Book One"

    assert book_two.title == "Book Two"
    assert len(book_two.clippings) == 1
    assert book_two.clippings[0].content == "Note from Book Two"

    assert result == [
        ImportedBookDTO(
            title="Book One",
            authors="Author One",
            imported_clippings_count=1,
            is_new=True,
        ),
        ImportedBookDTO(
            title="Book Two",
            authors="Author Two",
            imported_clippings_count=1,
            is_new=True,
        ),
    ]


async def test_update_existing_book_with_new_clipping(
    sut, mother, mock_clipping_reader, mock_book_storage
):
    # Arrange
    await mock_book_storage.add(
        mother.book(
            id="1",
            title="The Book",
            authors=["The Author"],
            clippings=[
                mother.clipping(
                    id="existing-id", page=(1, 1), content="Existing Clipping"
                )
            ],
        )
    )
    mock_clipping_reader.clippings = [
        mother.clipping_import_candidate_dto(
            book_title="The Book",
            book_authors=["The Author"],
            page=(10, 10),
            type=ClippingType.HIGHLIGHT,
            content="New Clipping",
            added_at=datetime(2024, 8, 12),
        )
    ]

    # Act
    result = await sut.execute(user_id="user:42")

    # Assert
    updated_book = await mock_book_storage.get("1")
    assert len(updated_book.clippings) == 2
    assert updated_book.clippings[1].content == "New Clipping"

    assert result == [
        ImportedBookDTO(
            title="The Book",
            authors="The Author",
            imported_clippings_count=1,
            is_new=False,
        )
    ]


async def test_no_new_clippings_should_not_update_books(
    sut, mother, mock_clipping_reader, mock_book_storage
):
    # Arrange
    await mock_book_storage.add(
        mother.book(
            id="1",
            title="The Book",
            authors=["The Author"],
            clippings=[mother.clipping(id="existing-id", content="Existing Clipping")],
        )
    )
    mock_clipping_reader.clippings = []

    # Act
    result = await sut.execute(user_id="user:42")

    # Assert
    updated_book = await mock_book_storage.get("1")
    assert len(updated_book.clippings) == 1  # No new clippings added
    assert result == []  # No new books or clippings to update
