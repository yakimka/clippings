from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ButtonDTO:
    label: str
    url: str


@dataclass
class PaginationItemDTO:
    number: int
    current: bool
    url: str


@dataclass
class NotFoundDTO:
    page_title: str
    message: str
