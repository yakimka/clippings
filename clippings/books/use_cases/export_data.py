from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from clippings.books.entities import Book, DeletedHash
    from clippings.books.ports import BooksStorageABC, DeletedHashStorageABC


def book_json_serializer(book: Book) -> str:
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


def deleted_hash_json_serializer(deleted_hash: DeletedHash) -> str:
    serialized_hash = {
        "type": "deleted_hash",
        "id": deleted_hash.id,
    }
    return json.dumps(serialized_hash)


class ExportDataUseCase:
    def __init__(
        self,
        book_storage: BooksStorageABC,
        deleted_hash_storage: DeletedHashStorageABC,
        book_serializer: Callable[[Book], str] = book_json_serializer,
        deleted_hash_serializer: Callable[
            [DeletedHash], str
        ] = deleted_hash_json_serializer,
    ) -> None:
        self._book_storage = book_storage
        self._deleted_hash_storage = deleted_hash_storage
        self._book_serializer = book_serializer
        self._deleted_hash_serializer = deleted_hash_serializer

    async def execute(self) -> AsyncGenerator[str, None]:
        query = self._book_storage.FindQuery(start=0, limit=None)
        yield '{"version": 1}'
        async for book in self._book_storage.find_iter(query):
            yield self._book_serializer(book)

        for deleted_hash in await self._deleted_hash_storage.get_all():
            yield self._deleted_hash_serializer(deleted_hash)
