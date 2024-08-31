from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass
class Book:
    id: str
    title: str
    author: str | None
    cover_url: str | None
    clippings: list[Clipping]
    review: str = ""
    rating: int | None = None

    def __post_init__(self):
        self.link_notes()

    def get_clipping(self, clipping_id: str) -> Clipping | None:
        for clipping in self.clippings:
            if clipping.id == clipping_id:
                return clipping
        return None

    def add_clippings(self, clippings: list[Clipping]) -> None:
        existed_ids = set()
        for clipping in self.clippings:
            existed_ids.add(clipping.id)
            # for inline_note in clipping.inline_notes:
            #     existed_ids.add(inline_note.id)

        for clipping in clippings:
            if clipping.id not in existed_ids:
                self.clippings.append(clipping)

        self.link_notes()

    def link_notes(self) -> None:
        self.clippings.sort(key=lambda cl: cl.position_id)
        position_to_highlight: dict[tuple[int, int], Clipping] = {}
        position_to_note: dict[tuple[int, int], tuple[Clipping, int]] = {}
        to_delete = []
        for i, clipping in enumerate(self.clippings):
            if clipping.type == ClippingType.HIGHLIGHT:
                position_to_highlight[clipping.position_id] = clipping
                if prev := position_to_note.pop(clipping.position_id, None):
                    prev_note, note_i = prev
                    clipping.inline_notes.append(
                        InlineNote(
                            id=prev_note.id,
                            content=prev_note.content,
                            automatically_linked=True,
                            added_at=prev_note.added_at,
                        )
                    )
                    to_delete.append(note_i)
            elif clipping.type == ClippingType.NOTE:
                if prev_hl := position_to_highlight.get(clipping.position_id):
                    prev_hl.inline_notes.append(
                        InlineNote(
                            id=clipping.id,
                            content=clipping.content,
                            automatically_linked=True,
                            added_at=clipping.added_at,
                        )
                    )
                    to_delete.append(i)
                else:
                    position_to_note[clipping.position_id] = (clipping, i)

        for i in reversed(to_delete):
            del self.clippings[i]


class ClippingType(Enum):
    HIGHLIGHT = "highlight"
    NOTE = "note"
    UNLINKED_NOTE = "unlinked_note"


@dataclass
class InlineNote:
    id: str
    content: str
    automatically_linked: bool
    added_at: datetime


@dataclass
class Clipping:
    id: str
    page: tuple[int, int]
    location: tuple[int, int]
    type: ClippingType
    content: str
    inline_notes: list[InlineNote]
    added_at: datetime

    @property
    def position_id(self) -> tuple[int, int]:
        return self.page[0], self.location[0]

    def get_inline_note(self, note_id: str) -> InlineNote | None:
        for note in self.inline_notes:
            if note.id == note_id:
                return note
        return None

    def add_inline_note(self, content: str) -> None:
        self.inline_notes.append(
            InlineNote(
                id=str(len(self.inline_notes) + 1),
                content=content,
                automatically_linked=False,
                added_at=datetime.now(),
            )
        )

    def remove_inline_note(self, note_id: str) -> None:
        self.inline_notes = [note for note in self.inline_notes if note.id != note_id]
