from dataclasses import dataclass

from clippings.books.entities import Clipping, ClippingType
from clippings.books.ports import BooksStorageABC


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
    def __init__(self, book_storage: BooksStorageABC):
        self._book_storage = book_storage

    async def execute(self, book_id: str, clipping_id: str, content: str) -> None:
        book = await self._book_storage.get(book_id)
        clipping = book.get_clipping(clipping_id)
        clipping.add_inline_note(content)
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
        clipping = book.get_clipping(clipping_id)
        inline_note = clipping.get_inline_note(inline_note_id)
        book.add_clippings(
            [
                Clipping(
                    id=inline_note.id,
                    page=clipping.page,
                    location=clipping.location,
                    type=ClippingType.UNLINKED_NOTE,
                    content=inline_note.content,
                    inline_notes=[],
                    added_at=inline_note.added_at,
                )
            ]
        )
        clipping.remove_inline_note(inline_note_id)
        await self._book_storage.add(book)
