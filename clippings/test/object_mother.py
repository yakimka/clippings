from datetime import datetime

from clippings.domain.books import Author, Book
from clippings.domain.clippings import Clipping, ClippingType


class ObjectMother:  # noqa: PIE798
    @classmethod
    def clipping(
        cls,
        *,
        id: str = "clipping:id",
        page: int = 1,
        location: tuple[int, int] = (10, 22),
        type: ClippingType = ClippingType.HIGHLIGHT,
        book_id: str = "book:id",
        content: str = "some highlighted text",
        created_at: datetime = datetime(2024, 8, 9),  # noqa: B008
    ) -> Clipping:
        return Clipping(
            id=id,
            page=page,
            location=location,
            type=type,
            book_id=book_id,
            content=content,
            created_at=created_at,
        )

    @classmethod
    def book(
        cls,
        *,
        id: str = "book:id",
        title: str = "The Book",
        author_id: str = "author:id",
    ) -> Book:
        return Book(id=id, title=title, author_id=author_id)

    @classmethod
    def author(
        cls,
        *,
        id: str = "author:id",
        name: str = "The Author",
    ) -> Author:
        return Author(id=id, name=name)
