from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clippings.books.entities import Book, Clipping, DeletedHash
from clippings.books.services import (
    EnrichBooksMetaService,
    check_book_limit,
    check_clippings_per_book_limit,
)
from clippings.seedwork.exceptions import CantFindEntityError

if TYPE_CHECKING:
    from clippings.books.ports import (
        BookIdGenerator,
        BooksStorageABC,
        ClippingIdGenerator,
        ClippingsReaderABC,
        DeletedHashStorageABC,
        InlineNoteIdGenerator,
    )
    from clippings.users.ports import UsersStorageABC


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
        enrich_books_meta_service: EnrichBooksMetaService,
        book_id_generator: BookIdGenerator,
        clipping_id_generator: ClippingIdGenerator,
        inline_note_id_generator: InlineNoteIdGenerator,
        users_storage: UsersStorageABC,
    ) -> None:
        self._storage = storage
        self._reader = reader
        self._deleted_hash_storage = deleted_hash_storage
        self._enrich_books_meta_service = enrich_books_meta_service
        self._book_id_generator = book_id_generator
        self._clipping_id_generator = clipping_id_generator
        self._inline_note_id_generator = inline_note_id_generator
        self._users_storage = users_storage

    async def execute(self, user_id: str) -> list[ImportedBookDTO]:  # noqa: C901
        user = await self._users_storage.get(user_id)
        if not user:
            raise CantFindEntityError(f"User with id '{user_id}' not found.")

        book_id_to_book_map: dict[str, Book] = {}
        book_id_to_clippings_map: dict[str, list[Clipping]] = {}
        deleted_hashes = await self._deleted_hash_storage.get_all()
        async for candidate in self._reader.read():
            book_id = self._book_id_generator(candidate.book)
            if book_id not in book_id_to_book_map:
                book_id_to_book_map[book_id] = Book(
                    id=book_id,
                    title=candidate.book.title,
                    authors=candidate.book.authors or [Book.UNKNOWN_AUTHOR],
                    meta=None,
                    clippings=[],
                )
            clipping = Clipping(
                id=self._clipping_id_generator(candidate),
                page=candidate.page,
                location=candidate.location,
                type=candidate.type,
                content=candidate.content,
                added_at=candidate.added_at,
                inline_notes=[],
            )
            clipping_deleted_hash = DeletedHash.from_ids(
                book_id, clipping_id=clipping.id
            )
            if clipping_deleted_hash in deleted_hashes:
                continue
            book_id_to_clippings_map.setdefault(book_id, []).append(clipping)

        books_from_storage = await self._storage.get_many(list(book_id_to_book_map))
        books_from_storage_by_id = {book.id: book for book in books_from_storage}

        to_update: list[Book] = []
        books_to_add_meta = []
        statistics: list[ImportedBookDTO] = []
        for candidate_book_id, book in book_id_to_book_map.items():
            new_clippings = book_id_to_clippings_map.get(candidate_book_id, [])
            if existed_book := books_from_storage_by_id.get(candidate_book_id):
                if new_clippings:
                    check_clippings_per_book_limit(
                        user,
                        book_current_clipping_count=len(existed_book.clippings),
                        clippings_being_added_count=len(new_clippings),
                        book_title=existed_book.title,
                    )
                if added := existed_book.add_clippings(new_clippings):
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

                if new_clippings:
                    check_clippings_per_book_limit(
                        user,
                        book_current_clipping_count=0,
                        clippings_being_added_count=len(new_clippings),
                        book_title=book.title,
                    )

                # Add clippings (even if empty, to create the book object
                # if it's truly new and not filtered)
                # The add_clippings method handles the actual addition.
                # If new_clippings is empty, len(book.clippings) will be 0.
                book.add_clippings(new_clippings)

                if new_clippings:
                    to_update.append(book)
                    books_to_add_meta.append(book)
                    statistics.append(
                        ImportedBookDTO(
                            title=book.title,
                            authors=book.authors_to_str(),
                            imported_clippings_count=len(book.clippings),
                            is_new=True,
                        )
                    )

        if books_to_add_meta:
            current_user_book_count = await self._storage.count(
                self._storage.FindQuery()
            )
            check_book_limit(user, current_user_book_count, len(books_to_add_meta))

        await self._enrich_books_meta_service.execute(books_to_add_meta)
        for book in to_update:
            book.link_notes(inline_note_id_generator=self._inline_note_id_generator)

        if to_update:
            await self._storage.extend(to_update)
        return statistics
