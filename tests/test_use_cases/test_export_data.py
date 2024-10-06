import json

import pytest

from clippings.books.entities import ClippingType
from clippings.books.use_cases.export_data import ExportDataUseCase


@pytest.fixture()
def make_sut(mock_book_storage):
    def _make_sut():
        return ExportDataUseCase(mock_book_storage)

    return _make_sut


async def test_first_entry_is_export_metadata(make_sut, mock_book_storage, mother):
    sut = make_sut()
    book = mother.book()
    await mock_book_storage.add(book)

    result = sut.execute()
    data = [item async for item in result]

    assert data
    assert json.loads(data[0]) == {"version": 1}


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

    result = sut.execute()
    data = [item async for item in result]

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

    result = sut.execute()
    data = [item async for item in result]

    assert len(data) == 4  # 1 metadata + 3 books
