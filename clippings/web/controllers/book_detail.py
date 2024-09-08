from picodi import Provide, inject

from clippings.books.ports import BooksStorageABC
from clippings.web.deps import get_books_storage
from clippings.web.presenters.book.detail.page import (
    BookDetailPagePart,
    BookDetailPagePresenter,
    ClippingPresenter,
)
from clippings.web.presenters.dtos import PresenterResult
from clippings.web.presenters.urls import urls_manager


class BaseBookDetailRenderController:
    part: BookDetailPagePart

    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, book_id: str) -> PresenterResult:
        presenter = BookDetailPagePresenter(
            storage=self._books_storage, urls_manager=urls_manager
        )
        return await presenter.present(book_id=book_id, part=self.part)


class RenderBookDetailPageController(BaseBookDetailRenderController):
    part = BookDetailPagePart.ALL


class RenderBookInfoController(BaseBookDetailRenderController):
    part = BookDetailPagePart.INFO


class RenderBookReviewController(BaseBookDetailRenderController):
    part = BookDetailPagePart.REVIEW


class RenderBookClippingListController(BaseBookDetailRenderController):
    part = BookDetailPagePart.CLIPPINGS


class RenderBookClippingDetailController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, book_id: str, clipping_id: str) -> PresenterResult:
        presenter = ClippingPresenter(
            storage=self._books_storage, urls_manager=urls_manager
        )
        return await presenter.present(book_id=book_id, clipping_id=clipping_id)
