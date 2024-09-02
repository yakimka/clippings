from __future__ import annotations

from dataclasses import dataclass

from clippings.books.presenters.dtos import ActionDTO


@dataclass(kw_only=True)
class ClippingDataDTO:
    content: str
    type: str
    page: str
    location: str
    added_at: str
    notes_label: str
    inline_notes: list[InlineNoteDTO]


@dataclass
class InlineNoteDTO:
    id: str
    content: str
    actions: list[ActionDTO]
