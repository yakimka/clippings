from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, TypeAlias

from clippings.books.exceptions import CantFindEntityError
from clippings.seedwork.exceptions import DomainError

if TYPE_CHECKING:
    from datetime import datetime

    from clippings.books.ports import InlineNoteIdGenerator


@dataclass
class Book:
    id: str
    title: str
    authors: list[str]
    cover_url: str | None
    clippings: list[Clipping]
    review: str = ""
    rating: int | None = None

    def authors_to_str(self) -> str:
        return " & ".join(self.authors)

    def authors_from_str(self, authors: str) -> None:
        self.authors = authors.split(" & ")

    def get_clipping(self, clipping_id: str) -> Clipping | None:
        for clipping in self.clippings:
            if clipping.id == clipping_id:
                return clipping
        return None

    def remove_clipping(self, clipping: Clipping) -> None:
        for i, item in enumerate(self.clippings):
            if clipping.id == item.id:
                del self.clippings[i]
                break

    def add_clippings(self, clippings: list[Clipping]) -> int:
        existed_ids = set()
        for clipping in self.clippings:
            existed_ids.add(clipping.id)
            for inline_note in clipping.inline_notes:
                if inline_note.original_id:
                    existed_ids.add(inline_note.original_id)

        added_count = 0
        for clipping in clippings:
            if clipping.id not in existed_ids:
                self.clippings.append(clipping)
                added_count += 1
                existed_ids.add(clipping.id)
        self._sort_clippings_in_reading_order()
        return added_count

    def _sort_clippings_in_reading_order(self) -> None:
        clipping_type_order = {
            ClippingType.HIGHLIGHT: 0,
            ClippingType.NOTE: 1,
            ClippingType.UNLINKED_NOTE: 1,
        }
        self.clippings.sort(
            key=lambda cl: (cl.position_id, clipping_type_order[cl.type])
        )

    def link_notes(self, *, inline_note_id_generator: InlineNoteIdGenerator) -> None:
        self._sort_clippings_in_reading_order()
        pos_to_highlight: dict[Position, Clipping] = {}
        to_delete = []
        for i, cl in enumerate(self.clippings):
            if cl.type == ClippingType.HIGHLIGHT:
                pos_to_highlight[cl.position_id] = cl
            elif cl.type == ClippingType.NOTE and cl.position_id in pos_to_highlight:
                prev_hl = pos_to_highlight[cl.position_id]
                prev_hl.inline_notes.append(
                    InlineNote.create_from_clipping(
                        cl, id_generator=inline_note_id_generator
                    )
                )
                to_delete.append(i)

        for i in reversed(to_delete):
            del self.clippings[i]

    def unlink_inline_note(
        self, clipping_id: str, inline_note_id: str
    ) -> None | DomainError:
        clipping = self.get_clipping(clipping_id)
        if clipping is None:
            return CantFindEntityError(f"Clipping with id {clipping_id} not found")
        inline_note = clipping.get_inline_note(inline_note_id)
        if inline_note is None:
            return CantFindEntityError(
                f"Inline note with id {inline_note_id} not found"
            )

        new_clipping = clipping.restore(inline_note)
        if isinstance(new_clipping, DomainError):
            return new_clipping
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


Position: TypeAlias = tuple[int, int]


@dataclass
class Clipping:
    id: str
    page: Position
    location: Position
    type: ClippingType
    content: str
    inline_notes: list[InlineNote]
    added_at: datetime

    @property
    def position_id(self) -> Position:
        return self.page[0], self.location[0]

    def get_inline_note(self, note_id: str) -> InlineNote | None:
        for note in self.inline_notes:
            if note.id == note_id:
                return note
        return None

    def add_inline_note(self, inline_note: InlineNote) -> None:
        self.inline_notes.append(inline_note)

    def restore(self, inline_note: InlineNote) -> Clipping | DomainError:
        if not inline_note.automatically_linked or not inline_note.original_id:
            return DomainError("Can't restore not autolinked note")
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
