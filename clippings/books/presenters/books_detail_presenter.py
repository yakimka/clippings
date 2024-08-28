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


class BooksDetailPresenter:
    def __init__(self, storage: BooksStorageABC) -> None:
        self._storage = storage

    async def present(
        self,
        book_id: str,
        edit_review_form_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/review/edit"
        ),
        edit_book_info_form_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/info/edit",
        ),
        add_clipping: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/clippings", method="post"
        ),
        add_inline_note: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/clippings/{clipping_id}/inline_notes",
            method="post",
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
                            ),
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
                    ],
                )
            )

        return BooksDetailDTO(
            page_title=f"{book.title} Clippings",
            actions=[
                ActionDTO(
                    id="edit_book_info",
                    label="edit",
                    url=UrlDTO.from_template(edit_book_info_form_url, book_id=book_id),
                ),
                ActionDTO(
                    id="edit_review",
                    label="edit" if book.review else "Add review",
                    url=UrlDTO.from_template(edit_review_form_url, book_id=book_id),
                ),
            ],
            cover_url="https://placehold.co/400x600",
            title=book.title,
            author=f"by {book.author}",
            rating="No rating" if book.rating is None else f"Rating: {book.rating}/10",
            review=book.review,
            notes_label="Notes",
            clippings=clippings,
        )

    async def book_info(
        self,
        book_id: str,
        edit_book_info_form_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/info/edit"
        ),
    ) -> BookInfoDTO | NotFoundDTO:
        book = await self._storage.get(book_id)
        if book is None:
            return NotFoundDTO(
                page_title="Book not found",
                message="The book you are looking for does not exist.",
            )

        return BookInfoDTO(
            cover_url="https://placehold.co/400x600",
            title=book.title,
            author=f"by {book.author}",
            rating="No rating" if book.rating is None else f"Rating: {book.rating}/10",
            actions=[
                ActionDTO(
                    id="edit_book_info",
                    label="edit",
                    url=UrlDTO.from_template(edit_book_info_form_url, book_id=book_id),
                )
            ],
        )

    async def edit_book_info(
        self,
        book_id: str,
        book_info_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/info", method="patch"
        ),
        cancel_edit_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/info"
        ),
    ) -> BookEditInfoDTO | NotFoundDTO:
        book = await self._storage.get(book_id)
        if book is None:
            return NotFoundDTO(
                page_title="Book not found",
                message="The book you are looking for does not exist.",
            )

        return BookEditInfoDTO(
            cover_url="https://placehold.co/400x600",
            title=book.title,
            author=book.author,
            rating=str(book.rating),
            fields_meta={
                "title": {"label": "Book Title"},
                "author": {"label": "Author"},
                "rating": {"label": "Rating", "min": 0, "max": 10},
                "cover": {"label": "Upload cover"},
            },
            actions=[
                ActionDTO(
                    id="edit_book_info",
                    label="Save",
                    url=UrlDTO.from_template(book_info_url, book_id=book_id),
                ),
                ActionDTO(
                    id="cancel_edit",
                    label="Cancel",
                    url=UrlDTO.from_template(cancel_edit_url, book_id=book_id),
                ),
            ],
        )

    async def review(
        self,
        book_id: str,
        edit_review_form_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/review/edit"
        ),
    ) -> BookReviewDTO | NotFoundDTO:
        book = await self._storage.get(book_id)
        if book is None:
            return NotFoundDTO(
                page_title="Book not found",
                message="The book you are looking for does not exist.",
            )

        return BookReviewDTO(
            review=book.review,
            actions=[
                ActionDTO(
                    id="edit_review",
                    label="edit" if book.review else "Add review",
                    url=UrlDTO.from_template(edit_review_form_url, book_id=book_id),
                ),
            ],
        )

    async def edit_review(
        self,
        book_id: str,
        book_edit_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/review", method="patch"
        ),
        cancel_edit_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/review"
        ),
    ) -> BookReviewDTO | NotFoundDTO:
        book = await self._storage.get(book_id)
        if book is None:
            return NotFoundDTO(
                page_title="Book not found",
                message="The book you are looking for does not exist.",
            )

        return BookReviewDTO(
            review=book.review,
            actions=[
                ActionDTO(
                    id="edit_review",
                    label="Save",
                    url=UrlDTO.from_template(book_edit_url, book_id=book_id),
                ),
                ActionDTO(
                    id="cancel_edit",
                    label="Cancel",
                    url=UrlDTO.from_template(cancel_edit_url, book_id=book_id),
                ),
            ],
        )


class BooksDetailStringRenderedABC(abc.ABC):
    @abc.abstractmethod
    async def render(self, dto: BooksDetailDTO | NotFoundDTO) -> str:
        pass


class BooksDetailHtmlRendered(BooksDetailStringRenderedABC):
    def __init__(self) -> None:
        self._template_name = "books_detail/page.jinja2"
        self._env = jinja_env

    async def render(self, dto: BooksDetailDTO | NotFoundDTO) -> str:
        return self._env.get_template(self._template_name).render(data=dto)


class BookReviewHtmlRendered(BooksDetailStringRenderedABC):
    def __init__(self) -> None:
        self._template_name = "books_detail/review.jinja2"
        self._env = jinja_env

    async def render(self, dto: BooksDetailDTO | NotFoundDTO) -> str:
        return self._env.get_template(self._template_name).render(data=dto)


class EditReviewFormHtmlRendered(BooksDetailStringRenderedABC):
    def __init__(self) -> None:
        self._template_name = "books_detail/edit_review_form.jinja2"
        self._env = jinja_env

    async def render(self, dto: BooksDetailDTO | NotFoundDTO) -> str:
        return self._env.get_template(self._template_name).render(data=dto)


class BookInfoHtmlRendered(BooksDetailStringRenderedABC):
    def __init__(self) -> None:
        self._template_name = "books_detail/book_info.jinja2"
        self._env = jinja_env

    async def render(self, dto: BooksDetailDTO | NotFoundDTO) -> str:
        return self._env.get_template(self._template_name).render(data=dto)


class EditInfoFormHtmlRendered(BooksDetailStringRenderedABC):
    def __init__(self) -> None:
        self._template_name = "books_detail/edit_book_info_form.jinja2"
        self._env = jinja_env

    async def render(self, dto: BooksDetailDTO | NotFoundDTO) -> str:
        return self._env.get_template(self._template_name).render(data=dto)
