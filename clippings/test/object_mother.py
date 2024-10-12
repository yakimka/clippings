from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from clippings.books.dtos import BookDTO, ClippingImportCandidateDTO
from clippings.books.entities import (
    Book,
    BookMeta,
    Clipping,
    ClippingType,
    DeletedHash,
    InlineNote,
    Position,
)
from clippings.users.entities import User
from clippings.utils.hash import hasher

if TYPE_CHECKING:
    from collections.abc import Iterable

    from clippings.users.ports import PasswordHasherABC


class ObjectMother:
    def __init__(self, user_password_hasher: PasswordHasherABC) -> None:
        self.user_password_hasher = user_password_hasher

    def book(
        self,
        *,
        id: str = "book:id",
        title: str = "The Book",
        authors: Iterable[str] = ("The Author",),
        meta: BookMeta | None = None,
        review: str = "",
        rating: int | None = None,
        clippings: list[Clipping] | None = None,
    ) -> Book:
        if clippings is None:
            clippings = []
        return Book(
            id=id,
            title=title,
            authors=list(authors),
            meta=meta or self.book_meta(),
            clippings=clippings,
            review=review,
            rating=rating,
        )

    def book_meta(
        self,
        *,
        isbns: Iterable[str] = ("1234567890",),
        cover_image_small: str = "https://placehold.co/100x150",
        cover_image_big: str = "https://placehold.co/400x600",
    ) -> BookMeta:
        return BookMeta(
            isbns=list(isbns),
            cover_image_small=cover_image_small,
            cover_image_big=cover_image_big,
        )

    def clipping(
        self,
        *,
        id: str = "clipping:id",
        page: Position = (1, 1),
        location: Position = (10, 22),
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

    def inline_note(
        self,
        *,
        id: str = "inline_note:id",
        content: str = "some note",
        original_id: str | None = "in:orig_id",
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

    def clipping_import_candidate_dto(
        self,
        book_title: str = "The Book",
        book_authors: Iterable[str] = ("The Author",),
        page: Position = (1, 1),
        location: Position = (10, 22),
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

    def deleted_hash(self, *, id: str = "hash") -> DeletedHash:
        return DeletedHash(id=id)

    def hashed_id(self, text: str, /) -> str:
        return hasher(text)

    def user(
        self,
        *,
        id: str = "user:42",
        nickname: str = "my_nickname",
        hashed_password: str | None = None,
    ) -> User:
        return User(id=id, nickname=nickname, hashed_password=hashed_password)
