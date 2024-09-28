from __future__ import annotations

from typing import TYPE_CHECKING

from picodi import Provide, inject

from clippings.books.adapters.id_generators import inline_note_id_generator
from clippings.books.use_cases.edit_book import (
    AddInlineNoteUseCase,
    ClippingFieldsDTO,
    DeleteBookUseCase,
    DeleteClippingUseCase,
    DeleteInlineNoteUseCase,
    EditBookUseCase,
    EditClippingUseCase,
    EditInlineNoteUseCase,
    RatingDTO,
    ReviewDTO,
    TitleDTO,
    UnlinkInlineNoteUseCase,
)
from clippings.deps import get_books_storage, get_deleted_hash_storage
from clippings.seedwork.exceptions import DomainError
from clippings.web.controllers.responses import HTMLResponse, RedirectResponse, Response
from clippings.web.presenters.book.detail.forms import (
    AddInlineNoteFormPresenter,
    EditBookInfoFormPresenter,
    EditBookReviewFormPresenter,
    EditClippingFormPresenter,
    EditInlineNoteFormPresenter,
)
from clippings.web.presenters.urls import urls_manager

if TYPE_CHECKING:
    from clippings.books.ports import BooksStorageABC, DeletedHashStorageABC


class RenderBookReviewEditFormController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, book_id: str) -> HTMLResponse:
        presenter = EditBookReviewFormPresenter(
            storage=self._books_storage, urls_manager=urls_manager
        )
        result = await presenter.present(book_id=book_id)
        return HTMLResponse.from_presenter_result(result)


class RenderBookInfoEditFormController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, book_id: str) -> HTMLResponse:
        presenter = EditBookInfoFormPresenter(
            storage=self._books_storage, urls_manager=urls_manager
        )
        result = await presenter.present(book_id=book_id)
        return HTMLResponse.from_presenter_result(result)


class RenderBookClippingEditFormController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, book_id: str, clipping_id: str) -> HTMLResponse:
        presenter = EditClippingFormPresenter(
            storage=self._books_storage, urls_manager=urls_manager
        )
        result = await presenter.present(book_id=book_id, clipping_id=clipping_id)
        return HTMLResponse.from_presenter_result(result)


class RenderInlineNoteAddFromController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, book_id: str, clipping_id: str) -> HTMLResponse:
        presenter = AddInlineNoteFormPresenter(
            storage=self._books_storage, urls_manager=urls_manager
        )
        result = await presenter.present(book_id=book_id, clipping_id=clipping_id)
        return HTMLResponse.from_presenter_result(result)


class RenderInlineNoteEditFormController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(
        self, book_id: str, clipping_id: str, inline_note_id: str
    ) -> HTMLResponse:
        presenter = EditInlineNoteFormPresenter(
            storage=self._books_storage, urls_manager=urls_manager
        )
        result = await presenter.present(
            book_id=book_id, clipping_id=clipping_id, inline_note_id=inline_note_id
        )
        return HTMLResponse.from_presenter_result(result)


class UpdateBookReviewController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, book_id: str, review: str) -> Response:
        use_case = EditBookUseCase(book_storage=self._books_storage)
        result = await use_case.execute(
            book_id=book_id, fields=[ReviewDTO(review=review)]
        )
        if isinstance(result, DomainError):
            return HTMLResponse(payload=str(result))

        redirect = urls_manager.build_url("book_review", book_id=book_id)
        return RedirectResponse(url=redirect.value, status_code=303)


class UpdateBookInfoController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(
        self, book_id: str, title: str, authors: str, rating: int | None
    ) -> Response:
        use_case = EditBookUseCase(book_storage=self._books_storage)
        result = await use_case.execute(
            book_id=book_id,
            fields=[
                TitleDTO(title=title, authors=authors),
                RatingDTO(rating=rating),
            ],
        )
        if isinstance(result, DomainError):
            return HTMLResponse(payload=str(result))

        redirect = urls_manager.build_url("book_info", book_id=book_id)
        return RedirectResponse(url=redirect.value, status_code=303)


class UpdateClippingController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, book_id: str, clipping_id: str, content: str) -> Response:
        use_case = EditClippingUseCase(book_storage=self._books_storage)
        result = await use_case.execute(
            ClippingFieldsDTO(
                id=clipping_id,
                book_id=book_id,
                content=content,
            )
        )
        if isinstance(result, DomainError):
            return HTMLResponse(payload=str(result))

        redirect = urls_manager.build_url(
            "clipping_detail", book_id=book_id, clipping_id=clipping_id
        )
        return RedirectResponse(url=redirect.value, status_code=303)


class AddInlineNoteController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, book_id: str, clipping_id: str, content: str) -> Response:
        use_case = AddInlineNoteUseCase(
            book_storage=self._books_storage,
            inline_note_id_generator=inline_note_id_generator,
        )
        result = await use_case.execute(
            book_id=book_id, clipping_id=clipping_id, content=content
        )
        if isinstance(result, DomainError):
            return HTMLResponse(payload=str(result))

        redirect = urls_manager.build_url(
            "clipping_detail", book_id=book_id, clipping_id=clipping_id
        )
        return RedirectResponse(url=redirect.value, status_code=303)


class EditInlineNoteController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(
        self, book_id: str, clipping_id: str, inline_note_id: str, content: str
    ) -> Response:
        use_case = EditInlineNoteUseCase(book_storage=self._books_storage)
        result = await use_case.execute(
            book_id=book_id,
            clipping_id=clipping_id,
            inline_note_id=inline_note_id,
            content=content,
        )
        if isinstance(result, DomainError):
            return HTMLResponse(payload=str(result))

        redirect = urls_manager.build_url(
            "clipping_detail",
            book_id=book_id,
            clipping_id=clipping_id,
            inline_note_id=inline_note_id,
        )
        return RedirectResponse(url=redirect.value, status_code=303)


class UnlinkInlineNoteController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(
        self, book_id: str, clipping_id: str, inline_note_id: str
    ) -> Response:
        use_case = UnlinkInlineNoteUseCase(book_storage=self._books_storage)
        result = await use_case.execute(
            book_id=book_id,
            clipping_id=clipping_id,
            inline_note_id=inline_note_id,
        )
        if isinstance(result, DomainError):
            return HTMLResponse(payload=str(result))

        redirect = urls_manager.build_url(
            "clipping_list",
            book_id=book_id,
            clipping_id=clipping_id,
            inline_note_id=inline_note_id,
        )
        return RedirectResponse(url=redirect.value, status_code=303)


class DeleteBookController:
    @inject
    def __init__(
        self,
        books_storage: BooksStorageABC = Provide(get_books_storage),
        deleted_hash_storage: DeletedHashStorageABC = Provide(get_deleted_hash_storage),
    ) -> None:
        self._books_storage = books_storage
        self._deleted_hash_storage = deleted_hash_storage

    async def fire(self, book_id: str) -> HTMLResponse:
        use_case = DeleteBookUseCase(
            book_storage=self._books_storage,
            deleted_hash_storage=self._deleted_hash_storage,
        )
        result = await use_case.execute(book_id)
        if isinstance(result, DomainError):
            return HTMLResponse(payload=str(result))
        return HTMLResponse(payload="", status_code=200)


class DeleteClippingController:
    @inject
    def __init__(
        self,
        books_storage: BooksStorageABC = Provide(get_books_storage),
        deleted_hash_storage: DeletedHashStorageABC = Provide(get_deleted_hash_storage),
    ) -> None:
        self._books_storage = books_storage
        self._deleted_hash_storage = deleted_hash_storage

    async def fire(self, book_id: str, clipping_id: str) -> HTMLResponse:
        use_case = DeleteClippingUseCase(
            book_storage=self._books_storage,
            deleted_hash_storage=self._deleted_hash_storage,
        )
        result = await use_case.execute(book_id, clipping_id)
        if isinstance(result, DomainError):
            return HTMLResponse(payload=str(result))
        return HTMLResponse(payload="", status_code=200)


class DeleteInlineNoteController:
    @inject
    def __init__(
        self,
        books_storage: BooksStorageABC = Provide(get_books_storage),
        deleted_hash_storage: DeletedHashStorageABC = Provide(get_deleted_hash_storage),
    ) -> None:
        self._books_storage = books_storage
        self._deleted_hash_storage = deleted_hash_storage

    async def fire(
        self, book_id: str, clipping_id: str, inline_note_id: str
    ) -> Response:
        use_case = DeleteInlineNoteUseCase(
            book_storage=self._books_storage,
            deleted_hash_storage=self._deleted_hash_storage,
        )
        result = await use_case.execute(
            book_id=book_id,
            clipping_id=clipping_id,
            inline_note_id=inline_note_id,
        )
        if isinstance(result, DomainError):
            return HTMLResponse(payload=str(result))

        redirect = urls_manager.build_url(
            "clipping_detail",
            book_id=book_id,
            clipping_id=clipping_id,
            inline_note_id=inline_note_id,
        )
        return RedirectResponse(url=redirect.value, status_code=303)
