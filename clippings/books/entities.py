from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass
class Book:
    id: str
    title: str
    author: Author
    clippings: list[Clipping]


@dataclass
class Author:
    id: str
    name: str


class ClippingType(Enum):
    HIGHLIGHT = "highlight"
    NOTE = "note"


@dataclass
class Clipping:
    id: str
    page: int
    location: tuple[int, int]
    type: ClippingType
    content: str
    added_at: datetime
