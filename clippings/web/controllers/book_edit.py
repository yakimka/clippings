from picodi import Provide, inject

from clippings.books.ports import BooksStorageABC
from clippings.web.deps import get_books_storage
from clippings.web.presenters.book.detail.forms import (
    AddInlineNoteFormPresenter,
    EditBookInfoFormPresenter,
    EditBookReviewFormPresenter,
    EditClippingFormPresenter,
    EditInlineNoteFormPresenter,
)
from clippings.web.presenters.dtos import PresenterResult
from clippings.web.presenters.urls import urls_manager


class RenderBookReviewEditFormController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, book_id: str) -> PresenterResult:
        presenter = EditBookReviewFormPresenter(
            storage=self._books_storage, urls_manager=urls_manager
        )
        return await presenter.present(book_id=book_id)


class RenderBookInfoEditFormController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, book_id: str) -> PresenterResult:
        presenter = EditBookInfoFormPresenter(
            storage=self._books_storage, urls_manager=urls_manager
        )
        return await presenter.present(book_id=book_id)


class RenderBookClippingEditFormController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, book_id: str, clipping_id: str) -> PresenterResult:
        presenter = EditClippingFormPresenter(
            storage=self._books_storage, urls_manager=urls_manager
        )
        return await presenter.present(book_id=book_id, clipping_id=clipping_id)


class RenderInlineNoteAddFromController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, book_id: str, clipping_id: str) -> PresenterResult:
        presenter = AddInlineNoteFormPresenter(
            storage=self._books_storage, urls_manager=urls_manager
        )
        return await presenter.present(book_id=book_id, clipping_id=clipping_id)


class RenderInlineNoteEditFormController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(
        self, book_id: str, clipping_id: str, inline_note_id: str
    ) -> PresenterResult:
        presenter = EditInlineNoteFormPresenter(
            storage=self._books_storage, urls_manager=urls_manager
        )
        return await presenter.present(
            book_id=book_id, clipping_id=clipping_id, inline_note_id=inline_note_id
        )
