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
        add_clipping: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/clippings", method="post"
        ),
        add_inline_note: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/clippings/{clipping_id}/inline_notes", method="post"
        ),
        edit_clipping_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/clippings/{clipping_id}", method="put"
        ),
        delete_clipping_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/clippings/{clipping_id}", method="delete"
        ),
        unlink_inline_note_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/clippings/{clipping_id}", method="post"
        ),
    ) -> BooksDetailDTO | NotFoundDTO:
        book = await self._storage.get(book_id)
        if book is None:
            return NotFoundDTO(
                page_title="Book not found",
                message="The book you are looking for does not exist.",
            )

        clippings = []
        for clipping in book.clippings:
            inline_notes = []
            for inline_note in clipping.inline_notes:
                inline_note_dto = InlineNoteDTO(
                    id=inline_note.id,
                    content=inline_note.content,
                    actions=[
                        ActionDTO(
                            id="edit_clipping",
                            label="edit",
                            url=UrlDTO.from_template(
                                edit_clipping_url,
                                book_id=book_id,
                                clipping_id=inline_note.id,
                            ),
                        ),
                        ActionDTO(
                            id="delete_clipping",
                            label="delete",
                            url=UrlDTO.from_template(
                                delete_clipping_url,
                                book_id=book_id,
                                clipping_id=inline_note.id,
                            ),
                        ),
                    ],
                )
                if inline_note.automatically_linked:
                    inline_note_dto.actions.append(
                        ActionDTO(
                            id="unlink_inline_note",
                            label="unlink",
                            url=UrlDTO.from_template(
                                unlink_inline_note_url,
                                book_id=book_id,
                                clipping_id=inline_note.id,
                            ),
                        )
                    )
                inline_notes.append(inline_note_dto)

            clippings.append(
                ClippingDTO(
                    content=clipping.content,
                    type=clipping.type.value.capitalize(),
                    page=f"Page: {"-".join(map(str, clipping.page))}",
                    location=f"Loc: {"-".join(map(str, clipping.location))}",
                    added_at=f"Added: {clipping.added_at.date().isoformat()}",
                    inline_notes=inline_notes,
                    actions=[
                        ActionDTO(
                            id="add_inline_note",
                            label="add note",
                            url=UrlDTO.from_template(
                                add_inline_note,
                                book_id=book_id,
                                clipping_id=clipping.id,
                            )
                        ),
                        ActionDTO(
                            id="edit_clipping",
                            label="edit",
                            url=UrlDTO.from_template(
                                edit_clipping_url,
                                book_id=book_id,
                                clipping_id=clipping.id,
                            ),
                        ),
                        ActionDTO(
                            id="delete_clipping",
                            label="delete",
                            url=UrlDTO.from_template(
                                delete_clipping_url,
                                book_id=book_id,
                                clipping_id=clipping.id,
                            ),
                        ),
                    ]
                )
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
            clippings=clippings,
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
