from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from clippings.books.entities import ClippingType, Position


@dataclass
class BookDTO:
    title: str
    authors: list[str]


@dataclass
class ClippingImportCandidateDTO:
    book: BookDTO
    page: Position
    location: Position
    type: ClippingType
    content: str
    added_at: datetime


@dataclass
class BookInfoSearchResultDTO:
    isbns: list[str]
    title: str
    authors: list[str]
    cover_image_small: str | None
    cover_image_big: str | None
