from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clippings.web.presenters.dtos import ActionDTO


@dataclass(kw_only=True)
class ClippingDataDTO:
    content: str
    info: list[ClippingInfoDTO]
    notes_label: str
    inline_notes: list[InlineNoteDTO]


@dataclass
class ClippingInfoDTO:
    content: str


@dataclass
class InlineNoteDTO:
    id: str
    content: str
    actions: list[ActionDTO]
