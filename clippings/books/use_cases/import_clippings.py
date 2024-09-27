from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clippings.books.entities import Book, Clipping, DeletedHash

if TYPE_CHECKING:

    from clippings.books.ports import (
        BookIdGenerator,
        BooksStorageABC,
        ClippingIdGenerator,
        ClippingsReaderABC,
        DeletedHashStorageABC,
        InlineNoteIdGenerator,
    )


@dataclass
class ImportedBookDTO:
    title: str
    authors: str
    imported_clippings_count: int
    is_new: bool


class ImportClippingsUseCase:
    def __init__(
        self,
        storage: BooksStorageABC,
        reader: ClippingsReaderABC,
        deleted_hash_storage: DeletedHashStorageABC,
        book_id_generator: BookIdGenerator,
        clipping_id_generator: ClippingIdGenerator,
        inline_note_id_generator: InlineNoteIdGenerator,
    ) -> None:
        self._storage = storage
        self._reader = reader
        self._deleted_hash_storage = deleted_hash_storage
        self._book_id_generator = book_id_generator
        self._clipping_id_generator = clipping_id_generator
        self._inline_note_id_generator = inline_note_id_generator

    async def execute(self) -> list[ImportedBookDTO]:
        book_id_to_book_map: dict[str, Book] = {}
        async for candidate in self._reader.read():
            book_id = self._book_id_generator(candidate.book)
            if book_id not in book_id_to_book_map:
                book_id_to_book_map[book_id] = Book(
                    id=book_id,
                    title=candidate.book.title,
                    authors=candidate.book.authors or ["Unknown Author"],
                    cover_url=None,
                    clippings=[],
                )
            book_id_to_book_map[book_id].add_clippings(
                [
                    Clipping(
                        id=self._clipping_id_generator(candidate),
                        page=candidate.page,
                        location=candidate.location,
                        type=candidate.type,
                        content=candidate.content,
                        added_at=candidate.added_at,
                        inline_notes=[],
                    )
                ]
            )

        books_from_storage = await self._storage.get_many(list(book_id_to_book_map))
        books_from_storage_by_id = {book.id: book for book in books_from_storage}
        deleted_hashes = await self._deleted_hash_storage.get_all()

        to_update: list[Book] = []
        statistics: list[ImportedBookDTO] = []
        for candidate_book_id, book in book_id_to_book_map.items():
            if existed_book := books_from_storage_by_id.get(candidate_book_id):
                if added := existed_book.add_clippings(book.clippings):
                    to_update.append(existed_book)
                    statistics.append(
                        ImportedBookDTO(
                            title=existed_book.title,
                            authors=existed_book.authors_to_str(),
                            imported_clippings_count=added,
                            is_new=False,
                        )
                    )
            else:
                book_deleted_hash = DeletedHash.from_ids(book.id)
                if book_deleted_hash in deleted_hashes:
                    continue
                to_update.append(book)
                statistics.append(
                    ImportedBookDTO(
                        title=book.title,
                        authors=book.authors_to_str(),
                        imported_clippings_count=len(book.clippings),
                        is_new=True,
                    )
                )

        for book in to_update:
            book.link_notes(inline_note_id_generator=self._inline_note_id_generator)

        if to_update:
            await self._storage.extend(to_update)
        return statistics
