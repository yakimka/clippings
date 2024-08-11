from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from clippings.books.entities import ClippingType


@dataclass
class ClippingImportCandidateDTO:
    book_title: str
    book_author: str
    page: int
    location: tuple[int, int]
    type: ClippingType
    content: str
    added_at: datetime
