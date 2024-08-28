from datetime import datetime

from clippings.books.dtos import ClippingImportCandidateDTO
from clippings.books.entities import Book, Clipping, ClippingType, InlineNote


class ObjectMother:  # noqa: PIE798
    @classmethod
    def book(
        cls,
        *,
        id: str = "book:id",
        title: str = "The Book",
        author: str | None = "The Author",
        cover_url: str | None = "https://placehold.co/400x600",
        clippings: list[Clipping] | None = None,
    ) -> Book:
        if clippings is None:
            clippings = []
        return Book(
            id=id, title=title, author=author, cover_url=cover_url, clippings=clippings
        )

    @classmethod
    def clipping(
        cls,
        *,
        id: str = "clipping:id",
        page: tuple[int, int] = (1, 1),
        location: tuple[int, int] = (10, 22),
        type: ClippingType = ClippingType.HIGHLIGHT,
        content: str = "some highlighted text",
        added_at: datetime = datetime(2024, 8, 9),  # noqa: B008
        inline_notes: list[InlineNote] | None = None,
    ) -> Clipping:
        return Clipping(
            id=id,
            page=page,
            location=location,
            type=type,
            content=content,
            added_at=added_at,
            inline_notes=inline_notes or [],
        )

    @classmethod
    def inline_note(
        cls,
        *,
        id: str = "inline_note:id",
        content: str = "some note",
        added_at: datetime = datetime(2024, 8, 9),  # noqa: B008
    ) -> InlineNote:
        return InlineNote(id=id, content=content, added_at=added_at)

    @classmethod
    def clipping_import_candidate_dto(
        cls,
        book_title: str = "The Book",
        page: tuple[int, int] = (1, 1),
        location: tuple[int, int] = (10, 22),
        type: ClippingType = ClippingType.HIGHLIGHT,
        content: str = "The Content",
        added_at: datetime = datetime(2024, 8, 9),  # noqa: B008
    ) -> ClippingImportCandidateDTO:
        return ClippingImportCandidateDTO(
            book_title=book_title,
            page=page,
            location=location,
            type=type,
            content=content,
            added_at=added_at,
        )
