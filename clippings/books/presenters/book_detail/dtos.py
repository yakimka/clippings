from __future__ import annotations

from dataclasses import dataclass

from clippings.books.presenters.dtos import ActionDTO


@dataclass
class InlineNoteDTO:
    id: str
    content: str
    actions: list[ActionDTO]


@dataclass(kw_only=True)
class ClippingDataDTO:
    content: str
    type: str
    page: str
    location: str
    added_at: str
    notes_label: str
    inline_notes: list[InlineNoteDTO]


@dataclass(kw_only=True)
class ClippingDTO(ClippingDataDTO):
    actions: list[ActionDTO]

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}


@dataclass(kw_only=True)
class EditClippingDTO(ClippingDataDTO):
    content: str
    actions: list[ActionDTO]

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}


@dataclass(kw_only=True)
class AddInlineNoteDTO(ClippingDataDTO):
    actions: list[ActionDTO]

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}


@dataclass
class ClippingEditDTO:
    content: str
    actions: list[ActionDTO]

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}


@dataclass
class BookDetailDTO:
    page_title: str
    actions: list[ActionDTO]
    cover_url: str
    title: str
    author: str
    rating: str
    review: str
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


@dataclass
class ClippingAddDTO:
    type: str
    page: str
    location: str
    book_id: str
    actions: list[ActionDTO]

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}


@dataclass
class EditInlineNoteDTO:
    content: str
    actions: list[ActionDTO]

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}
