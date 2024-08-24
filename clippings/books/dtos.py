from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from clippings.books.entities import ClippingType


@dataclass(kw_only=True, frozen=True)
class ClippingImportCandidateDTO:
    book_title: str
    page: tuple[int, int]
    location: tuple[int, int]
    type: ClippingType
    content: str
    added_at: datetime
