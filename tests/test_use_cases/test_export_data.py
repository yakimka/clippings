import json

import pytest

from clippings.books.entities import ClippingType
from clippings.books.use_cases.export_data import ExportDataUseCase


@pytest.fixture()
def make_sut(mock_book_storage, mock_deleted_hash_storage):
    def _make_sut():
        return ExportDataUseCase(
            mock_book_storage, deleted_hash_storage=mock_deleted_hash_storage
        )

    return _make_sut


async def test_first_entry_is_export_metadata(make_sut, mock_book_storage, mother):
    sut = make_sut()
    book = mother.book()
    await mock_book_storage.add(book)

    result = await sut.execute()
    data = [item async for item in result.iterator]

    assert data
    assert json.loads(data[0]) == {"version": "1"}


async def test_export_one_book(make_sut, mock_book_storage, mother):
    sut = make_sut()
    book = mother.book(
        id="book_id",
        title="Book Title",
        authors=["Author 1", "Author 2"],
        meta=mother.book_meta(
            isbns=["01234567890"],
            cover_image_small="https://placehold.co/100x150",
            cover_image_big="https://placehold.co/400x600",
        ),
        review="Book review",
        rating=5,
        clippings=[
            mother.clipping(
                id="clipping_id",
                page=(1, 1),
                location=(10, 22),
                type=ClippingType.HIGHLIGHT,
                content="Clipping content",
                inline_notes=[
                    mother.inline_note(
                        id="note_id",
                        content="Note content",
                        original_id="original_id",
                        automatically_linked=True,
                    ),
                ],
            )
        ],
    )
    await mock_book_storage.add(book)

    result = await sut.execute()
    data = [item async for item in result.iterator]

    assert result.version
    assert result.started_at
    assert result.filename
    assert data
    exported_book = json.loads(data[-1])
    assert exported_book == {
        "type": "book",
        "id": "book_id",
        "title": "Book Title",
        "authors": ["Author 1", "Author 2"],
        "review": "Book review",
        "rating": 5,
        "clippings": [
            {
                "id": "clipping_id",
                "page": [1, 1],
                "location": [10, 22],
                "type": "highlight",
                "content": "Clipping content",
                "added_at": "2024-08-09T00:00:00",
                "inline_notes": [
                    {
                        "id": "note_id",
                        "content": "Note content",
                        "original_id": "original_id",
                        "automatically_linked": True,
                    }
                ],
            }
        ],
    }


async def test_export_multiple_books(make_sut, mock_book_storage, mother):
    sut = make_sut()
    books = [mother.book(id=f"book_id_{i}") for i in range(3)]
    await mock_book_storage.extend(books)

    result = await sut.execute()
    data = [item async for item in result.iterator]

    assert len(data) == 4  # 1 metadata + 3 books


async def test_exported_data_must_be_delimited_by_newline(
    make_sut, mock_book_storage, mother
):
    sut = make_sut()
    books = [mother.book(id=f"book_id_{i}") for i in range(3)]
    await mock_book_storage.extend(books)

    result = await sut.execute()
    data = [item async for item in result.iterator]

    assert all(item.endswith("\n") for item in data)


async def test_export_deleted_hashes(make_sut, mother, mock_deleted_hash_storage):
    sut = make_sut()
    deleted_hash = mother.deleted_hash(id="deleted_hash")
    await mock_deleted_hash_storage.add(deleted_hash)

    result = await sut.execute()
    data = [item async for item in result.iterator]

    assert data
    assert json.loads(data[-1]) == {"type": "deleted_hash", "id": "deleted_hash"}


async def test_export_all_entities_at_once(
    make_sut, mother, mock_book_storage, mock_deleted_hash_storage
):
    sut = make_sut()
    book = mother.book(id="book_id")
    deleted_hash = mother.deleted_hash(id="deleted_hash")
    await mock_book_storage.add(book)
    await mock_deleted_hash_storage.add(deleted_hash)

    result = await sut.execute()
    data = [item async for item in result.iterator]

    assert len(data) == 3  # 1 metadata + 1 book + 1 deleted hash
