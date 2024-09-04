from __future__ import annotations

from typing import TYPE_CHECKING

from clippings.books.entities import Book, Clipping

if TYPE_CHECKING:

    from clippings.books.ports import (
        BookIdGenerator,
        BooksStorageABC,
        ClippingIdGenerator,
        ClippingsReaderABC,
        InlineNoteIdGenerator,
    )


class ImportClippingsUseCase:
    def __init__(
        self,
        storage: BooksStorageABC,
        reader: ClippingsReaderABC,
        book_id_generator: BookIdGenerator,
        clipping_id_generator: ClippingIdGenerator,
        inline_note_id_generator: InlineNoteIdGenerator,
    ):
        self._storage = storage
        self._reader = reader
        self._book_id_generator = book_id_generator
        self._clipping_id_generator = clipping_id_generator
        self._inline_note_id_generator = inline_note_id_generator

    async def execute(self) -> None:
        book_id_to_book_map: dict[str, Book] = {}
        async for candidate in self._reader.read():
            book_id = self._book_id_generator(candidate.book)
            if book_id not in book_id_to_book_map:
                book_id_to_book_map[book_id] = Book(
                    id=book_id,
                    title=candidate.book.title,
                    author=candidate.book.author,
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

        to_update: list[Book] = []
        for candidate_book_id, book in book_id_to_book_map.items():
            if existed_book := books_from_storage_by_id.get(candidate_book_id):
                if existed_book.add_clippings(book.clippings):
                    to_update.append(existed_book)
            else:
                to_update.append(book)

        for book in to_update:
            book.link_notes(inline_note_id_generator=self._inline_note_id_generator)

        await self._storage.extend(to_update)
