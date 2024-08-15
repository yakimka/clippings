from datetime import datetime

from clippings.books.dtos import ClippingImportCandidateDTO
from clippings.books.entities import Author, Book, Clipping, ClippingType


class ObjectMother:  # noqa: PIE798
    @classmethod
    def book(
        cls,
        *,
        id: str = "book:id",
        title: str = "The Book",
        author: Author | None = None,
        clippings: list[Clipping] | None = None,
    ) -> Book:
        if author is None:
            author = cls.author()
        if clippings is None:
            clippings = []
        return Book(id=id, title=title, author=author, clippings=clippings)

    @classmethod
    def clipping(
        cls,
        *,
        id: str = "clipping:id",
        page: int = 1,
        location: tuple[int, int] = (10, 22),
        type: ClippingType = ClippingType.HIGHLIGHT,
        content: str = "some highlighted text",
        added_at: datetime = datetime(2024, 8, 9),  # noqa: B008
    ) -> Clipping:
        return Clipping(
            id=id,
            page=page,
            location=location,
            type=type,
            content=content,
            added_at=added_at,
        )

    @classmethod
    def author(
        cls,
        *,
        id: str = "author:id",
        name: str = "The Author",
    ) -> Author:
        return Author(id=id, name=name)

    @classmethod
    def clipping_import_candidate_dto(
        cls,
        book_title: str = "The Book",
        page: int = 1,
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
