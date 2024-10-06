from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from clippings.books.entities import Book
    from clippings.books.ports import BooksStorageABC


def json_serializer(book: Book) -> str:
    serialized_book = {
        "type": "book",
        "id": book.id,
        "title": book.title,
        "authors": book.authors,
        "review": book.review,
        "rating": book.rating,
        "clippings": [
            {
                "id": clipping.id,
                "page": list(clipping.page),
                "location": list(clipping.location),
                "type": clipping.type.value,
                "content": clipping.content,
                "added_at": clipping.added_at.isoformat(),
                "inline_notes": [
                    {
                        "id": note.id,
                        "content": note.content,
                        "original_id": note.original_id,
                        "automatically_linked": note.automatically_linked,
                    }
                    for note in clipping.inline_notes
                ],
            }
            for clipping in book.clippings
        ],
    }
    return json.dumps(serialized_book)


class ExportDataUseCase:
    def __init__(
        self,
        book_storage: BooksStorageABC,
        serializer: Callable[[Book], str] = json_serializer,
    ) -> None:
        self._book_storage = book_storage
        self._serializer = serializer

    async def execute(self) -> AsyncGenerator[str, None]:
        query = self._book_storage.FindQuery(start=0, limit=None)
        yield '{"version": 1}'
        async for book in self._book_storage.find_iter(query):
            yield self._serializer(book)
