from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from clippings.books.entities import InlineNote

if TYPE_CHECKING:
    from clippings.books.ports import BooksStorageABC, InlineNoteIdGenerator


@dataclass
class BookFieldsDTO:
    id: str
    title: str | None = None
    author: str | None = None
    cover_url: str | None = None
    rating: int | None = None
    review: str | None = None


class EditBookUseCase:
    def __init__(self, book_storage: BooksStorageABC):
        self._book_storage = book_storage

    async def execute(self, data: BookFieldsDTO) -> None:
        book = await self._book_storage.get(data.id)
        to_patch = {}
        if data.title is not None:
            to_patch["title"] = data.title
        if data.author is not None:
            to_patch["author"] = data.author
        if data.cover_url is not None:
            to_patch["cover_url"] = data.cover_url
        if data.rating is not None:
            to_patch["rating"] = data.rating
        if data.review is not None:
            to_patch["review"] = data.review

        if not to_patch:
            return

        for field, value in to_patch.items():
            setattr(book, field, value)

        await self._book_storage.add(book)


@dataclass
class ClippingFieldsDTO:
    id: str
    book_id: str
    content: str | None = None


class EditClippingUseCase:
    def __init__(self, book_storage: BooksStorageABC):
        self._book_storage = book_storage

    async def execute(self, data: ClippingFieldsDTO) -> None:
        book = await self._book_storage.get(data.book_id)
        clipping = book.get_clipping(data.id)
        to_patch = {}
        if data.content is not None:
            to_patch["content"] = data.content

        if not to_patch:
            return

        for field, value in to_patch.items():
            setattr(clipping, field, value)

        await self._book_storage.add(book)


class AddInlineNoteUseCase:
    def __init__(
        self,
        book_storage: BooksStorageABC,
        inline_note_id_generator: InlineNoteIdGenerator,
    ):
        self._book_storage = book_storage
        self._inline_note_id_generator = inline_note_id_generator

    async def execute(self, book_id: str, clipping_id: str, content: str) -> None:
        book = await self._book_storage.get(book_id)
        clipping = book.get_clipping(clipping_id)
        inline_note = InlineNote.create(
            content=content,
            added_at=datetime.now(),
            id_generator=self._inline_note_id_generator,
        )
        clipping.add_inline_note(inline_note)
        await self._book_storage.add(book)


class EditInlineNoteUseCase:
    def __init__(self, book_storage: BooksStorageABC):
        self._book_storage = book_storage

    async def execute(
        self, book_id: str, clipping_id: str, inline_note_id: str, content: str
    ) -> None:
        book = await self._book_storage.get(book_id)
        clipping = book.get_clipping(clipping_id)
        inline_note = clipping.get_inline_note(inline_note_id)
        inline_note.content = content
        await self._book_storage.add(book)


class DeleteInlineNoteUseCase:
    def __init__(self, book_storage: BooksStorageABC):
        self._book_storage = book_storage

    async def execute(
        self, book_id: str, clipping_id: str, inline_note_id: str
    ) -> None:
        book = await self._book_storage.get(book_id)
        clipping = book.get_clipping(clipping_id)
        clipping.remove_inline_note(inline_note_id)
        await self._book_storage.add(book)


class UnlinkInlineNoteUseCase:
    def __init__(self, book_storage: BooksStorageABC):
        self._book_storage = book_storage

    async def execute(
        self, book_id: str, clipping_id: str, inline_note_id: str
    ) -> None:
        book = await self._book_storage.get(book_id)

        book.unlink_inline_note(clipping_id, inline_note_id)
        await self._book_storage.add(book)
