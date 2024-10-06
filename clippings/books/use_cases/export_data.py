from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, AsyncIterable, Callable

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


@dataclass
class ExportDataDTO:
    version: str
    iterator: AsyncIterable[str]
    started_at: datetime
    filename: str


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
        self._version = "1"

    async def execute(self) -> ExportDataDTO:
        date_now = datetime.now()
        return ExportDataDTO(
            version=self._version,
            iterator=self._generate_data(),
            started_at=date_now,
            filename=f"my-clippings-{date_now.strftime('%Y-%m-%d_%H-%M-%S')}.ndjson",
        )

    async def _generate_data(self) -> AsyncGenerator[str, None]:
        query = self._book_storage.FindQuery(start=0, limit=None)
        yield self._format_item(json.dumps({"version": self._version}))
        async for book in self._book_storage.find_iter(query):
            yield self._format_item(self._book_serializer(book))

        for deleted_hash in await self._deleted_hash_storage.get_all():
            yield self._format_item(self._deleted_hash_serializer(deleted_hash))

    def _format_item(self, item: str) -> str:
        return f"{item}\n"
