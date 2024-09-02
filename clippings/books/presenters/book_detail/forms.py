from clippings.books.ports import BooksStorageABC
from clippings.books.presenters.book_detail.dto_builder import BookDetailBuilder
from clippings.books.presenters.book_detail.dtos import (
    AddInlineNoteDTO,
    BookEditInfoDTO,
    BookReviewDTO,
    EditClippingDTO,
    EditInlineNoteDTO,
)
from clippings.books.presenters.dtos import (
    ActionDTO,
    NotFoundPresenterResult,
    PresenterResult,
)
from clippings.books.presenters.html_renderers import make_html_renderer
from clippings.books.presenters.urls import UrlsManager


class EditBookInfoFormPresenter:
    def __init__(
        self,
        storage: BooksStorageABC,
        urls_manager: UrlsManager,
    ) -> None:
        self._storage = storage
        self._urls_manager = urls_manager

    async def present(
        self, book_id: str
    ) -> PresenterResult[BookEditInfoDTO] | NotFoundPresenterResult:
        book = await self._storage.get(book_id)
        if book is None:
            return PresenterResult.not_found()
        builder = BookDetailBuilder(book, self._urls_manager)

        data = BookEditInfoDTO(
            cover_url=builder.cover_url(),
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
                    id="save",
                    label="Save",
                    url=self._urls_manager.build_url(
                        "book_info_update", book_id=book_id
                    ),
                ),
                ActionDTO(
                    id="cancel",
                    label="Cancel",
                    url=self._urls_manager.build_url("book_info", book_id=book_id),
                ),
            ],
        )
        return PresenterResult(
            data=data, renderer=make_html_renderer("book_detail/forms/edit_info.jinja2")
        )


class EditBookReviewFormPresenter:
    def __init__(
        self,
        storage: BooksStorageABC,
        urls_manager: UrlsManager,
    ) -> None:
        self._storage = storage
        self._urls_manager = urls_manager

    async def present(
        self, book_id: str
    ) -> PresenterResult[BookReviewDTO] | NotFoundPresenterResult:
        book = await self._storage.get(book_id)
        if book is None:
            return PresenterResult.not_found()
        data = BookReviewDTO(
            review=book.review,
            actions=[
                ActionDTO(
                    id="save",
                    label="Save",
                    url=self._urls_manager.build_url(
                        "book_review_update", book_id=book_id
                    ),
                ),
                ActionDTO(
                    id="cancel",
                    label="Cancel",
                    url=self._urls_manager.build_url("book_review", book_id=book_id),
                ),
            ],
        )
        return PresenterResult(
            data=data,
            renderer=make_html_renderer("book_detail/forms/edit_review.jinja2"),
        )


class EditClippingFormPresenter:
    def __init__(
        self,
        storage: BooksStorageABC,
        urls_manager: UrlsManager,
    ) -> None:
        self._storage = storage
        self._urls_manager = urls_manager

    async def present(
        self, book_id: str, clipping_id: str
    ) -> PresenterResult[EditClippingDTO] | NotFoundPresenterResult:
        book = await self._storage.get(book_id)
        if book is None:
            return PresenterResult.not_found()

        clipping = book.get_clipping(clipping_id)
        if clipping is None:
            return PresenterResult.not_found()
        builder = BookDetailBuilder(book, self._urls_manager)
        clipping_data = builder.clipping_data_dto(clipping_id)

        data = EditClippingDTO(
            content=clipping.content,
            actions=[
                ActionDTO(
                    id="save",
                    label="Save",
                    url=self._urls_manager.build_url(
                        "clipping_update", book_id=book_id, clipping_id=clipping_id
                    ),
                ),
                ActionDTO(
                    id="cancel",
                    label="Cancel",
                    url=self._urls_manager.build_url(
                        "clipping_detail", book_id=book_id, clipping_id=clipping_id
                    ),
                ),
            ],
            type=clipping_data.type,
            page=clipping_data.page,
            location=clipping_data.location,
            added_at=clipping_data.added_at,
            notes_label=clipping_data.notes_label,
            inline_notes=clipping_data.inline_notes,
        )
        return PresenterResult(
            data=data,
            renderer=make_html_renderer("book_detail/forms/edit_clipping.jinja2"),
        )


class AddInlineNoteFormPresenter:
    def __init__(
        self,
        storage: BooksStorageABC,
        urls_manager: UrlsManager,
    ) -> None:
        self._storage = storage
        self._urls_manager = urls_manager

    async def present(
        self, book_id: str, clipping_id: str
    ) -> PresenterResult[AddInlineNoteDTO] | NotFoundPresenterResult:
        book = await self._storage.get(book_id)
        if book is None:
            return PresenterResult.not_found()
        builder = BookDetailBuilder(book, self._urls_manager)
        clipping_data = builder.clipping_data_dto(clipping_id)
        if clipping_data is None:
            return PresenterResult.not_found()

        data = AddInlineNoteDTO(
            actions=[
                ActionDTO(
                    id="save",
                    label="Save",
                    url=self._urls_manager.build_url(
                        "inline_note_add", book_id=book_id, clipping_id=clipping_id
                    ),
                ),
                ActionDTO(
                    id="cancel",
                    label="Cancel",
                    url=self._urls_manager.build_url(
                        "clipping_detail", book_id=book_id, clipping_id=clipping_id
                    ),
                ),
            ],
            content=clipping_data.content,
            type=clipping_data.type,
            page=clipping_data.page,
            location=clipping_data.location,
            added_at=clipping_data.added_at,
            notes_label=clipping_data.notes_label,
            inline_notes=clipping_data.inline_notes,
        )
        return PresenterResult(
            data=data,
            renderer=make_html_renderer("book_detail/forms/add_inline_note.jinja2"),
        )


class EditInlineNoteFormPresenter:
    def __init__(
        self,
        storage: BooksStorageABC,
        urls_manager: UrlsManager,
    ) -> None:
        self._storage = storage
        self._urls_manager = urls_manager

    async def present(
        self, book_id: str, clipping_id: str, inline_note_id: str
    ) -> PresenterResult[EditInlineNoteDTO] | NotFoundPresenterResult:
        book = await self._storage.get(book_id)
        if book is None:
            return PresenterResult.not_found()
        clipping = book.get_clipping(clipping_id)
        if clipping is None:
            return PresenterResult.not_found()
        inline_note = clipping.get_inline_note(inline_note_id)
        if inline_note is None:
            return PresenterResult.not_found()
        data = EditInlineNoteDTO(
            content=inline_note.content,
            actions=[
                ActionDTO(
                    id="save",
                    label="Save",
                    url=self._urls_manager.build_url(
                        "inline_note_update",
                        book_id=book_id,
                        clipping_id=clipping_id,
                        inline_note_id=inline_note_id,
                    ),
                ),
                ActionDTO(
                    id="cancel",
                    label="Cancel",
                    url=self._urls_manager.build_url(
                        "clipping_detail", book_id=book_id, clipping_id=clipping_id
                    ),
                ),
            ],
        )
        return PresenterResult(
            data=data,
            renderer=make_html_renderer("book_detail/forms/edit_inline_note.jinja2"),
        )
