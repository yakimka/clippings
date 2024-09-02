from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from clippings.books.ports import InlineNoteIdGenerator


@dataclass
class Book:
    id: str
    title: str
    author: str | None
    cover_url: str | None
    clippings: list[Clipping]
    review: str = ""
    rating: int | None = None

    def get_clipping(self, clipping_id: str) -> Clipping | None:
        for clipping in self.clippings:
            if clipping.id == clipping_id:
                return clipping
        return None

    def add_clippings(self, clippings: list[Clipping]) -> bool:
        existed_ids = set()
        for clipping in self.clippings:
            existed_ids.add(clipping.id)
            for inline_note in clipping.inline_notes:
                if inline_note.original_id:
                    existed_ids.add(inline_note.original_id)

        updated = False
        for clipping in clippings:
            if clipping.id not in existed_ids:
                self.clippings.append(clipping)
                updated = True
                existed_ids.add(clipping.id)
        return updated

    def link_notes(self, *, inline_note_id_generator: InlineNoteIdGenerator) -> None:
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
                        InlineNote.create_from_clipping(
                            prev_note, id_generator=inline_note_id_generator
                        )
                    )
                    to_delete.append(note_i)
            elif clipping.type == ClippingType.NOTE:
                if prev_hl := position_to_highlight.get(clipping.position_id):
                    prev_hl.inline_notes.append(
                        InlineNote.create_from_clipping(
                            clipping, id_generator=inline_note_id_generator
                        )
                    )
                    to_delete.append(i)
                else:
                    position_to_note[clipping.position_id] = (clipping, i)

        for i in reversed(to_delete):
            del self.clippings[i]

    def unlink_inline_note(
        self, clipping_id: str, inline_note_id: str
    ) -> None | Exception:
        clipping = self.get_clipping(clipping_id)
        inline_note = clipping.get_inline_note(inline_note_id)

        new_clipping = clipping.restore(inline_note)
        clipping.remove_inline_note(inline_note_id)
        self.add_clippings([new_clipping])
        return None


class ClippingType(Enum):
    HIGHLIGHT = "highlight"
    NOTE = "note"
    UNLINKED_NOTE = "unlinked_note"


@dataclass
class InlineNote:
    id: str
    content: str
    original_id: str | None
    automatically_linked: bool
    added_at: datetime

    @classmethod
    def create(
        cls, *, content: str, added_at: datetime, id_generator: InlineNoteIdGenerator
    ) -> InlineNote:
        return cls(
            id=id_generator(),
            content=content,
            original_id=None,
            automatically_linked=False,
            added_at=added_at,
        )

    @classmethod
    def create_from_clipping(
        cls, clipping: Clipping, *, id_generator: InlineNoteIdGenerator
    ) -> InlineNote:
        return cls(
            id=id_generator(),
            content=clipping.content,
            original_id=clipping.id,
            automatically_linked=True,
            added_at=clipping.added_at,
        )


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

    def add_inline_note(self, inline_note: InlineNote) -> None:
        self.inline_notes.append(inline_note)

    def restore(self, inline_note: InlineNote) -> Clipping:
        return Clipping(
            id=inline_note.original_id,
            page=self.page,
            location=self.location,
            type=ClippingType.UNLINKED_NOTE,
            content=inline_note.content,
            inline_notes=[],
            added_at=inline_note.added_at,
        )

    def remove_inline_note(self, note_id: str) -> None:
        self.inline_notes = [note for note in self.inline_notes if note.id != note_id]
