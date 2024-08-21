from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clippings.books.presenters import jinja_env
from clippings.books.presenters.dtos import (
    ActionDTO,
    NotFoundDTO,
    UrlDTO,
    UrlTemplateDTO,
)

if TYPE_CHECKING:
    from clippings.books.ports import BooksStorageABC


@dataclass
class InlineNoteDTO:
    id: str
    content: str


@dataclass
class ClippingDTO:
    content: str
    type: str
    page: str
    location: str
    added_at: str
    inline_notes: list[InlineNoteDTO]


@dataclass
class BooksDetailDTO:
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


class BooksDetailPresenter:
    def __init__(self, storage: BooksStorageABC) -> None:
        self._storage = storage

    async def present(
        self,
        book_id: str,
        upload_cover_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/upload_cover", method="post"
        ),
        find_cover_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/find_cover", method="post"
        ),
    ) -> BooksDetailDTO | NotFoundDTO:
        book = await self._storage.get(book_id)
        if book is None:
            return NotFoundDTO(
                page_title="Book not found",
                message="The book you are looking for does not exist.",
            )

        return BooksDetailDTO(
            page_title=f"{book.title} Clippings",
            actions=[
                ActionDTO(
                    id="upload_cover",
                    label="Upload cover",
                    url=UrlDTO.from_template(upload_cover_url, book_id=book_id),
                ),
                ActionDTO(
                    id="find_cover",
                    label="Find cover",
                    url=UrlDTO.from_template(find_cover_url, book_id=book_id),
                ),
            ],
            cover_url="https://placehold.co/400x600",
            title=book.title,
            author=f"by {book.author_name}",
            rating="Rating: 10/10",
            review="My review for this book",
            notes_label="Notes",
            clippings=[
                ClippingDTO(
                    content=clipping.content,
                    type=clipping.type.value.capitalize(),
                    page=f"Page: {"-".join(map(str, clipping.page))}",
                    location=f"Loc: {"-".join(map(str, clipping.location))}",
                    added_at=f"Added: {clipping.added_at.date().isoformat()}",
                    inline_notes=[
                        InlineNoteDTO(id=inline_note.id, content=inline_note.content)
                        for inline_note in clipping.inline_notes
                    ],
                )
                for clipping in book.clippings
            ],
        )


class BooksDetailStringRenderedABC(abc.ABC):
    @abc.abstractmethod
    async def render(self, dto: BooksDetailDTO | NotFoundDTO) -> str:
        pass


class BooksDetailHtmlRendered(BooksDetailStringRenderedABC):
    def __init__(self) -> None:
        self._template_name = "books_detail.jinja2"
        self._env = jinja_env

    async def render(self, dto: BooksDetailDTO | NotFoundDTO) -> str:
        return self._env.get_template(self._template_name).render(data=dto)
