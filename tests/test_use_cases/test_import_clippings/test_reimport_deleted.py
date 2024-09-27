import pytest

from clippings.books.adapters.id_generators import (
    clipping_id_generator,
    inline_note_id_generator,
)
from clippings.books.use_cases.edit_book import (
    DeleteBookUseCase,
    DeleteClippingUseCase,
    DeleteInlineNoteUseCase,
)
from clippings.books.use_cases.import_clippings import ImportClippingsUseCase


@pytest.fixture()
def import_clippings_use_case(
    mock_book_storage, mock_clipping_reader, autoincrement_id_generator
) -> ImportClippingsUseCase:
    return ImportClippingsUseCase(
        storage=mock_book_storage,
        reader=mock_clipping_reader,
        book_id_generator=autoincrement_id_generator,
        clipping_id_generator=clipping_id_generator,
        inline_note_id_generator=inline_note_id_generator,
    )


@pytest.fixture()
def delete_book_use_case(mock_book_storage):
    return DeleteBookUseCase(book_storage=mock_book_storage)


@pytest.fixture()
def delete_clipping_use_case(mock_book_storage):
    return DeleteClippingUseCase(book_storage=mock_book_storage)


@pytest.fixture()
def delete_inline_note_use_case(mock_book_storage):
    return DeleteInlineNoteUseCase(book_storage=mock_book_storage)


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
        )
    ]
    await import_clippings_use_case.execute()
    delete_result = await delete_book_use_case.execute("1")
    assert delete_result is None

    # Act
    await import_clippings_use_case.execute()

    # Assert
    all_books = await mock_book_storage.find()
    assert not all_books
