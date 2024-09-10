from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from clippings.books.entities import Book, InlineNote
from clippings.books.exceptions import CantFindEntityError, DomainError

if TYPE_CHECKING:
    from clippings.books.ports import BooksStorageABC, InlineNoteIdGenerator


@dataclass(kw_only=True)
class BookFieldDTO:
    def apply(self, book: Book) -> bool:
        raise NotImplementedError


@dataclass(kw_only=True)
class TitleDTO(BookFieldDTO):
    title: str
    authors: str

    def apply(self, book: Book) -> bool:
        changed = False
        if book.title != self.title:
            book.title = self.title
            changed = True
        if book.authors_to_str() != self.authors:
            book.authors_from_str(self.authors)
            changed = True
        return changed


@dataclass(kw_only=True)
class CoverUrlDTO(BookFieldDTO):
    cover_url: str | None

    def apply(self, book: Book) -> bool:
        if book.cover_url != self.cover_url:
            book.cover_url = self.cover_url
            return True
        return False


@dataclass(kw_only=True)
class RatingDTO(BookFieldDTO):
    rating: int | None

    def apply(self, book: Book) -> bool:
        if book.rating != self.rating:
            book.rating = self.rating
            return True
        return False


@dataclass(kw_only=True)
class ReviewDTO(BookFieldDTO):
    review: str

    def apply(self, book: Book) -> bool:
        if book.review != self.review:
            book.review = self.review
            return True
        return False


class EditBookUseCase:
    def __init__(self, book_storage: BooksStorageABC):
        self._book_storage = book_storage

    async def execute(
        self, book_id: str, fields: list[BookFieldDTO]
    ) -> None | DomainError:
        book = await self._book_storage.get(book_id)
        if book is None:
            return DomainError(f"Can't find book with id: {book_id}")

        changed = False
        for field in fields:
            if field.apply(book):
                changed = True
        if changed:
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


class DeleteBookUseCase:
    def __init__(self, book_storage: BooksStorageABC):
        self._book_storage = book_storage

    async def execute(self, book_id: str) -> None | DomainError:
        book = await self._book_storage.get(book_id)
        if book is None:
            return CantFindEntityError(f"Can't find book with id: {book_id}")
        await self._book_storage.remove(book)
        return None


class DeleteClippingUseCase:
    def __init__(self, book_storage: BooksStorageABC):
        self._book_storage = book_storage

    async def execute(self, book_id: str, clipping_id: str) -> None | DomainError:
        book = await self._book_storage.get(book_id)
        if book is None:
            return CantFindEntityError(f"Can't find book with id: {book_id}")
        if clipping := book.get_clipping(clipping_id):
            book.remove_clipping(clipping)
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
