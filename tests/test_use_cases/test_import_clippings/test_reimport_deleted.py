import pytest

from clippings.books.adapters.id_generators import (
    book_id_generator,
    clipping_id_generator,
    inline_note_id_generator,
)
from clippings.books.entities import ClippingType
from clippings.books.use_cases.edit_book import (
    DeleteBookUseCase,
    DeleteClippingUseCase,
    DeleteInlineNoteUseCase,
)
from clippings.books.use_cases.import_clippings import ImportClippingsUseCase


@pytest.fixture()
def import_clippings_use_case(
    mock_book_storage,
    mock_clipping_reader,
    mock_deleted_hash_storage,
    enrich_books_meta_service,
) -> ImportClippingsUseCase:
    return ImportClippingsUseCase(
        storage=mock_book_storage,
        reader=mock_clipping_reader,
        deleted_hash_storage=mock_deleted_hash_storage,
        enrich_books_meta_service=enrich_books_meta_service,
        book_id_generator=book_id_generator,
        clipping_id_generator=clipping_id_generator,
        inline_note_id_generator=inline_note_id_generator,
    )


@pytest.fixture()
def delete_book_use_case(mock_book_storage, mock_deleted_hash_storage):
    return DeleteBookUseCase(
        book_storage=mock_book_storage, deleted_hash_storage=mock_deleted_hash_storage
    )


@pytest.fixture()
def delete_clipping_use_case(mock_book_storage, mock_deleted_hash_storage):
    return DeleteClippingUseCase(
        book_storage=mock_book_storage, deleted_hash_storage=mock_deleted_hash_storage
    )


@pytest.fixture()
def delete_inline_note_use_case(mock_book_storage, mock_deleted_hash_storage):
    return DeleteInlineNoteUseCase(
        book_storage=mock_book_storage, deleted_hash_storage=mock_deleted_hash_storage
    )


async def test_reimporting_deleted_book_does_nothing(
    import_clippings_use_case,
    delete_book_use_case,
    mock_clipping_reader,
    mock_book_storage,
    mother,
):
    # Arrange
    mock_clipping_reader.clippings = [
        mother.clipping_import_candidate_dto(
            book_title="The Book",
            book_authors=["The Author"],
            content="The content",
        )
    ]
    await import_clippings_use_case.execute()
    imported_books = await mock_book_storage.find()
    assert len(imported_books) == 1

    # Act
    await delete_book_use_case.execute(imported_books[0].id)
    await import_clippings_use_case.execute()

    # Assert
    all_books = await mock_book_storage.find()
    assert not all_books


async def test_reimporting_deleted_clipping_does_nothing(
    import_clippings_use_case,
    delete_clipping_use_case,
    mock_clipping_reader,
    mock_book_storage,
    mother,
):
    # Arrange
    mock_clipping_reader.clippings = [
        mother.clipping_import_candidate_dto(
            book_title="The Book",
            book_authors=["The Author"],
            content="The content",
        )
    ]
    await import_clippings_use_case.execute()
    imported_books = await mock_book_storage.find()
    assert len(imported_books) == 1
    assert len(imported_books[0].clippings) == 1

    # Act
    await delete_clipping_use_case.execute(
        book_id=imported_books[0].id, clipping_id=imported_books[0].clippings[0].id
    )
    await import_clippings_use_case.execute()

    # Assert
    all_books = await mock_book_storage.find()
    assert len(all_books) == 1
    assert not all_books[0].clippings


async def test_reimporting_deleted_inline_note_does_nothing(
    import_clippings_use_case,
    delete_inline_note_use_case,
    mock_clipping_reader,
    mock_book_storage,
    mother,
):
    # Arrange
    mock_clipping_reader.clippings = [
        mother.clipping_import_candidate_dto(
            book_title="The Book",
            book_authors=["The Author"],
            content="The highlight content",
            type=ClippingType.HIGHLIGHT,
            location=(42, 102),
        ),
        mother.clipping_import_candidate_dto(
            book_title="The Book",
            book_authors=["The Author"],
            content="The note content",
            type=ClippingType.NOTE,
            location=(42, 42),
        ),
    ]
    await import_clippings_use_case.execute()
    imported_books = await mock_book_storage.find()
    assert len(imported_books) == 1
    assert len(imported_books[0].clippings) == 1
    assert len(imported_books[0].clippings[0].inline_notes) == 1

    # Act
    await delete_inline_note_use_case.execute(
        book_id=imported_books[0].id,
        clipping_id=imported_books[0].clippings[0].id,
        inline_note_id=imported_books[0].clippings[0].inline_notes[0].id,
    )
    await import_clippings_use_case.execute()

    # Assert
    all_books = await mock_book_storage.find()
    assert len(all_books) == 1
    assert len(all_books[0].clippings) == 1
    assert not all_books[0].clippings[0].inline_notes


async def test_reimporting_deleted_inline_note_which_deleted_with_clipping_does_nothing(
    import_clippings_use_case,
    delete_clipping_use_case,
    mock_clipping_reader,
    mock_book_storage,
    mother,
):
    # Arrange
    mock_clipping_reader.clippings = [
        mother.clipping_import_candidate_dto(
            book_title="The Book",
            book_authors=["The Author"],
            content="The highlight content",
            type=ClippingType.HIGHLIGHT,
            location=(42, 102),
        ),
        mother.clipping_import_candidate_dto(
            book_title="The Book",
            book_authors=["The Author"],
            content="The note content",
            type=ClippingType.NOTE,
            location=(42, 42),
        ),
    ]
    await import_clippings_use_case.execute()
    imported_books = await mock_book_storage.find()
    assert len(imported_books) == 1
    assert len(imported_books[0].clippings) == 1
    assert len(imported_books[0].clippings[0].inline_notes) == 1

    # Act
    await delete_clipping_use_case.execute(
        book_id=imported_books[0].id,
        clipping_id=imported_books[0].clippings[0].id,
    )
    await import_clippings_use_case.execute()

    # Assert
    all_books = await mock_book_storage.find()
    assert len(all_books) == 1
    assert not all_books[0].clippings
