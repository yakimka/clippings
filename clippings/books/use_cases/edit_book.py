from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from clippings.books.entities import InlineNote
from clippings.books.exceptions import CantFindEntityError, DomainError

if TYPE_CHECKING:
    from clippings.books.ports import BooksStorageABC, InlineNoteIdGenerator


@dataclass
class BookFieldsDTO:
    id: str
    title: str
    authors: list[str]
    cover_url: str | None = None
    rating: int | None = None
    review: str | None = None


class EditBookUseCase:
    def __init__(self, book_storage: BooksStorageABC):
        self._book_storage = book_storage

    async def execute(self, data: BookFieldsDTO) -> None | DomainError:
        book = await self._book_storage.get(data.id)
        if book is None:
            return DomainError(f"Can't find book with id: {data.id}")

        if data.title is not None:
            book.title = data.title
        if data.authors is not None:
            book.authors = data.authors
        if data.cover_url is not None:
            book.cover_url = data.cover_url
        if data.rating is not None:
            book.rating = data.rating
        if data.review is not None:
            book.review = data.review

        await self._book_storage.add(book)
        return None


@dataclass
class ClippingFieldsDTO:
    id: str
    book_id: str
    content: str


class EditClippingUseCase:
    def __init__(self, book_storage: BooksStorageABC):
        self._book_storage = book_storage

    async def execute(self, data: ClippingFieldsDTO) -> None | DomainError:
        book = await self._book_storage.get(data.book_id)
        if book is None:
            return CantFindEntityError(f"Can't find book with id: {data.book_id}")
        clipping = book.get_clipping(data.id)
        if clipping is None:
            return CantFindEntityError(
                f"Can't find clipping with id: {data.id}; Book id: {data.book_id}"
            )
        clipping.content = data.content
        await self._book_storage.add(book)
        return None


class AddInlineNoteUseCase:
    def __init__(
        self,
        book_storage: BooksStorageABC,
        inline_note_id_generator: InlineNoteIdGenerator,
    ):
        self._book_storage = book_storage
        self._inline_note_id_generator = inline_note_id_generator

    async def execute(
        self, book_id: str, clipping_id: str, content: str
    ) -> None | DomainError:
        book = await self._book_storage.get(book_id)
        if book is None:
            return CantFindEntityError(f"Can't find book with id: {book_id}")
        clipping = book.get_clipping(clipping_id)
        if clipping is None:
            return CantFindEntityError(
                f"Can't find clipping with id: {clipping_id} in book with id: {book_id}"
            )
        inline_note = InlineNote.create(
            content=content,
            added_at=datetime.now(),
            id_generator=self._inline_note_id_generator,
        )
        clipping.add_inline_note(inline_note)
        await self._book_storage.add(book)
        return None


class EditInlineNoteUseCase:
    def __init__(self, book_storage: BooksStorageABC):
        self._book_storage = book_storage

    async def execute(
        self, book_id: str, clipping_id: str, inline_note_id: str, content: str
    ) -> None | DomainError:
        book = await self._book_storage.get(book_id)
        if book is None:
            return CantFindEntityError(f"Can't find book with id: {book_id}")
        clipping = book.get_clipping(clipping_id)
        if clipping is None:
            return CantFindEntityError(
                f"Can't find clipping with id: {clipping_id} in book with id: {book_id}"
            )
        inline_note = clipping.get_inline_note(inline_note_id)
        if inline_note is None:
            return CantFindEntityError(
                f"Can't find inline note with id: {inline_note_id}"
            )
        inline_note.content = content
        await self._book_storage.add(book)
        return None


class DeleteInlineNoteUseCase:
    def __init__(self, book_storage: BooksStorageABC):
        self._book_storage = book_storage

    async def execute(
        self, book_id: str, clipping_id: str, inline_note_id: str
    ) -> None | DomainError:
        book = await self._book_storage.get(book_id)
        if book is None:
            return CantFindEntityError(f"Can't find book with id: {book_id}")
        clipping = book.get_clipping(clipping_id)
        if clipping is None:
            return CantFindEntityError(
                f"Can't find clipping with id: {clipping_id} in book with id: {book_id}"
            )
        clipping.remove_inline_note(inline_note_id)
        await self._book_storage.add(book)
        return None


class UnlinkInlineNoteUseCase:
    def __init__(self, book_storage: BooksStorageABC):
        self._book_storage = book_storage

    async def execute(
        self, book_id: str, clipping_id: str, inline_note_id: str
    ) -> None | DomainError:
        book = await self._book_storage.get(book_id)
        if book is None:
            return CantFindEntityError(f"Can't find book with id: {book_id}")

        book.unlink_inline_note(clipping_id, inline_note_id)
        await self._book_storage.add(book)
        return None
