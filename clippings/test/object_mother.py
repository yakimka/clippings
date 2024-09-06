from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from clippings.books.dtos import BookDTO, ClippingImportCandidateDTO
from clippings.books.entities import Book, Clipping, ClippingType, InlineNote

if TYPE_CHECKING:
    from collections.abc import Iterable


class ObjectMother:  # noqa: PIE798
    @classmethod
    def book(
        cls,
        *,
        id: str = "book:id",
        title: str = "The Book",
        authors: Iterable[str] = ("The Author",),
        cover_url: str | None = "https://placehold.co/400x600",
        clippings: list[Clipping] | None = None,
    ) -> Book:
        if clippings is None:
            clippings = []
        return Book(
            id=id,
            title=title,
            authors=list(authors),
            cover_url=cover_url,
            clippings=clippings,
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
        original_id: str = "inline_note:original_id",
        automatically_linked: bool = False,
        added_at: datetime = datetime(2024, 8, 9),  # noqa: B008
    ) -> InlineNote:
        return InlineNote(
            id=id,
            content=content,
            original_id=original_id,
            automatically_linked=automatically_linked,
            added_at=added_at,
        )

    @classmethod
    def clipping_import_candidate_dto(
        cls,
        book_title: str = "The Book",
        book_authors: Iterable[str] = ("The Author",),
        page: tuple[int, int] = (1, 1),
        location: tuple[int, int] = (10, 22),
        type: ClippingType = ClippingType.HIGHLIGHT,
        content: str = "The Content",
        added_at: datetime = datetime(2024, 8, 9),  # noqa: B008
    ) -> ClippingImportCandidateDTO:
        return ClippingImportCandidateDTO(
            book=BookDTO(title=book_title, authors=list(book_authors)),
            page=page,
            location=location,
            type=type,
            content=content,
            added_at=added_at,
        )
