from __future__ import annotations

from dataclasses import dataclass

from clippings.books.presenters.dtos import ActionDTO


@dataclass
class InlineNoteDTO:
    id: str
    content: str
    actions: list[ActionDTO]


@dataclass
class ClippingDTO:
    content: str
    type: str
    page: str
    location: str
    added_at: str
    inline_notes: list[InlineNoteDTO]
    actions: list[ActionDTO]


@dataclass
class BookDetailDTO:
    page_title: str
    actions: list[ActionDTO]
    cover_url: str
    title: str
    author: str
    rating: str
    review: str
    notes_label: str
    clippings: list[ClippingDTO]

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}


@dataclass(kw_only=True)
class BookInfoDTO:
    cover_url: str
    title: str
    author: str
    rating: str
    actions: list[ActionDTO]

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}


@dataclass(kw_only=True)
class BookEditInfoDTO(BookInfoDTO):
    fields_meta: dict[str, dict[str, str]]


@dataclass
class BookReviewDTO:
    review: str
    actions: list[ActionDTO]

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}
