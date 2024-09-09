from picodi import Provide, inject

from clippings.books.ports import BooksStorageABC
from clippings.books.use_cases.edit_book import EditBookUseCase, ReviewDTO
from clippings.web.controllers.responses import HTMLResponse, RedirectResponse
from clippings.web.deps import get_books_storage
from clippings.web.presenters.book.detail.forms import (
    AddInlineNoteFormPresenter,
    EditBookInfoFormPresenter,
    EditBookReviewFormPresenter,
    EditClippingFormPresenter,
    EditInlineNoteFormPresenter,
)
from clippings.web.presenters.urls import urls_manager


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

    async def fire(self, book_id: str, review: str) -> RedirectResponse:
        use_case = EditBookUseCase(book_storage=self._books_storage)
        await use_case.execute(book_id=book_id, fields=[ReviewDTO(review=review)])

        review_url = urls_manager.build_url("book_review", book_id=book_id)
        return RedirectResponse(url=review_url.value, status_code=303)
