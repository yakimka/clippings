from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import ANY

import pytest

from clippings.books.adapters.id_generators import (
    clipping_id_generator,
    inline_note_id_generator,
)
from clippings.books.entities import Book, Clipping, ClippingType
from clippings.books.use_cases.import_clippings import ImportClippingsUseCase

if TYPE_CHECKING:
    from clippings.books.ports import BookIdGenerator


@pytest.fixture()
def autoincrement_id_generator() -> BookIdGenerator:
    ids = (str(i) for i in range(1, 1000))
    return lambda _: str(next(ids))


@pytest.fixture()
def sut(
    mock_book_storage, mock_clipping_reader, autoincrement_id_generator
) -> ImportClippingsUseCase:
    return ImportClippingsUseCase(
        storage=mock_book_storage,
        reader=mock_clipping_reader,
        book_id_generator=autoincrement_id_generator,
        clipping_id_generator=clipping_id_generator,
        inline_note_id_generator=inline_note_id_generator,
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
    await sut.execute()

    # Assert
    book = await mock_book_storage.get("1")

    assert book == Book(
        id="1",
        title="The Book",
        authors=["The Author"],
        cover_url=None,
        clippings=[
            Clipping(
                id=ANY,
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

    await sut.execute()

    book = await mock_book_storage.get("1")
    assert book.authors == ["Unknown Author"]
