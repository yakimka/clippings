from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from clippings.books.entities import Book, ClippingType, Position
from clippings.web.presenters.book.detail.dtos import (
    ClippingDataDTO,
    ClippingInfoDTO,
    InlineNoteDTO,
)
from clippings.web.presenters.book.system_pages import (
    NotFoundDTO,
    not_found_page_presenter,
)
from clippings.web.presenters.dtos import ActionDTO, PresenterResult
from clippings.web.presenters.html_renderers import make_html_renderer
from clippings.web.presenters.image import image_or_default

if TYPE_CHECKING:
    from clippings.books.ports import BooksStorageABC
    from clippings.web.presenters.urls import UrlsManager


class BookDetailPagePart(Enum):
    ALL = "book/detail/page.jinja2"
    INFO = "book/detail/info.jinja2"
    REVIEW = "book/detail/review.jinja2"
    CLIPPINGS = "book/detail/clippings.jinja2"


@dataclass
class BookDetailDTO:
    page_title: str
    actions: list[ActionDTO]
    cover_url: str
    title: str
    authors: str
    rating: str
    review: str
    clippings: list[ClippingDTO]

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}


@dataclass(kw_only=True)
class ClippingDTO(ClippingDataDTO):
    info: list[ClippingInfoDTO]
    actions: list[ActionDTO]

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}


class BookDetailPagePresenter:
    def __init__(
        self,
        storage: BooksStorageABC,
        urls_manager: UrlsManager,
    ) -> None:
        self._storage = storage
        self._urls_manager = urls_manager

    async def present(
        self, book_id: str, part: BookDetailPagePart = BookDetailPagePart.ALL
    ) -> PresenterResult[BookDetailDTO] | PresenterResult[NotFoundDTO]:
        book = await self._storage.get(book_id)
        if book is None:
            return not_found_page_presenter()
        builder = BookDetailBuilder(book, self._urls_manager)

        return PresenterResult(
            data=builder.detail_dto(), renderer=make_html_renderer(part.value)
        )


class ClippingPresenter:
    def __init__(
        self,
        storage: BooksStorageABC,
        urls_manager: UrlsManager,
    ) -> None:
        self._storage = storage
        self._urls_manager = urls_manager

    async def present(
        self, book_id: str, clipping_id: str
    ) -> PresenterResult[ClippingDTO] | PresenterResult[NotFoundDTO]:
        book = await self._storage.get(book_id)
        if book is None:
            return not_found_page_presenter()
        clipping = book.get_clipping(clipping_id)
        if clipping is None:
            return not_found_page_presenter()
        builder = BookDetailBuilder(book, self._urls_manager)

        return PresenterResult(
            data=builder.clipping_dto(clipping_id),
            renderer=make_html_renderer("book/detail/clipping.jinja2"),
        )


class BookDetailBuilder:
    def __init__(self, book: Book, urls_manager: UrlsManager) -> None:
        self.book = book
        self.clippings_by_id = {clipping.id: clipping for clipping in book.clippings}
        self.inline_notes_by_id = {
            (cl.id, inl.id): inl for cl in book.clippings for inl in cl.inline_notes
        }
        self.urls_manager = urls_manager

    def detail_dto(self) -> BookDetailDTO:
        return BookDetailDTO(
            page_title=f"{self.book.title} Clippings",
            cover_url=self.cover_url_small(),
            title=self.book.title,
            authors=f"by {self.book.authors_to_str()}",
            rating=(
                "No rating"
                if self.book.rating is None
                else f"Rating: {self.book.rating}/10"
            ),
            review=self.book.review,
            clippings=[
                self.clipping_dto(clipping.id) for clipping in self.book.clippings
            ],
            actions=[
                ActionDTO(
                    id="book_info_update_form",
                    label="edit",
                    url=self.urls_manager.build_url(
                        "book_info_update_form", book_id=self.book.id
                    ),
                ),
                ActionDTO(
                    id="book_review_update_form",
                    label="edit" if self.book.review else "Add review",
                    url=self.urls_manager.build_url(
                        "book_review_update_form", book_id=self.book.id
                    ),
                ),
            ],
        )

    def cover_url_small(self) -> str:
        return image_or_default(
            getattr(self.book.meta, "cover_image_small", None), size="small"
        )

    def cover_url_big(self) -> str:
        return image_or_default(
            getattr(self.book.meta, "cover_image_big", None), size="big"
        )

    def clipping_data_dto(self, clipping_id: str) -> ClippingDataDTO:
        clipping = self.clippings_by_id[clipping_id]

        def format_position(position: Position) -> str:
            if position[0] == position[1]:
                return str(position[0])
            return f"{position[0]}-{position[1]}"

        clipping_type_map = {
            ClippingType.HIGHLIGHT: "Highlight",
            ClippingType.NOTE: "Note",
            ClippingType.UNLINKED_NOTE: "Note",
        }

        info = [
            ClippingInfoDTO(content=clipping_type_map[clipping.type]),
        ]
        if clipping.page != (-1, -1):
            info.append(
                ClippingInfoDTO(content=f"Page: {format_position(clipping.page)}")
            )
        if clipping.location != (-1, -1):
            info.append(
                ClippingInfoDTO(content=f"Loc: {format_position(clipping.location)}")
            )
        info.append(
            ClippingInfoDTO(content=f"Added: {clipping.added_at.date().isoformat()}")
        )

        return ClippingDataDTO(
            content=clipping.content,
            info=info,
            notes_label="Notes",
            inline_notes=[
                self._inline_note_dto(clipping_id, inline_note.id)
                for inline_note in clipping.inline_notes
            ],
        )

    def clipping_dto(self, clipping_id: str) -> ClippingDTO:
        clipping_data = self.clipping_data_dto(clipping_id)
        return ClippingDTO(
            content=clipping_data.content,
            info=clipping_data.info,
            notes_label=clipping_data.notes_label,
            inline_notes=clipping_data.inline_notes,
            actions=[
                ActionDTO(
                    id="inline_note_add",
                    label="add note",
                    url=self.urls_manager.build_url(
                        "inline_note_add_form",
                        book_id=self.book.id,
                        clipping_id=clipping_id,
                    ),
                ),
                ActionDTO(
                    id="clipping_update_form",
                    label="edit",
                    url=self.urls_manager.build_url(
                        "clipping_update_form",
                        book_id=self.book.id,
                        clipping_id=clipping_id,
                    ),
                ),
                ActionDTO(
                    id="clipping_delete",
                    label="delete",
                    confirm_message="Are you sure you want to delete this clipping?",
                    url=self.urls_manager.build_url(
                        "clipping_delete",
                        book_id=self.book.id,
                        clipping_id=clipping_id,
                    ),
                ),
            ],
        )

    def _inline_note_dto(self, clipping_id: str, inline_note_id: str) -> InlineNoteDTO:
        inline_note = self.inline_notes_by_id[(clipping_id, inline_note_id)]

        inline_note_dto = InlineNoteDTO(
            id=inline_note.id,
            content=inline_note.content,
            actions=[
                ActionDTO(
                    id="edit",
                    label="edit",
                    url=self.urls_manager.build_url(
                        "inline_note_update_form",
                        book_id=self.book.id,
                        clipping_id=clipping_id,
                        inline_note_id=inline_note.id,
                    ),
                ),
                ActionDTO(
                    id="delete",
                    label="delete",
                    confirm_message="Are you sure you want to delete this note?",
                    url=self.urls_manager.build_url(
                        "inline_note_delete",
                        book_id=self.book.id,
                        clipping_id=clipping_id,
                        inline_note_id=inline_note.id,
                    ),
                ),
            ],
        )
        if inline_note.automatically_linked:
            inline_note_dto.actions.append(
                ActionDTO(
                    id="unlink",
                    label="unlink",
                    confirm_message=(
                        "Are you sure you want to unlink this note from the highlight?"
                    ),
                    url=self.urls_manager.build_url(
                        "inline_note_unlink",
                        book_id=self.book.id,
                        clipping_id=clipping_id,
                        inline_note_id=inline_note.id,
                    ),
                )
            )
        return inline_note_dto
