from __future__ import annotations

from typing import TYPE_CHECKING

from picodi import Provide, inject

from clippings.deps import get_books_storage
from clippings.web.controllers.responses import HTMLResponse
from clippings.web.presenters.book.detail.page import (
    BookDetailPagePart,
    BookDetailPagePresenter,
    ClippingPresenter,
)
from clippings.web.presenters.urls import urls_manager

if TYPE_CHECKING:
    from clippings.books.ports import BooksStorageABC


class BaseBookDetailRenderController:
    part: BookDetailPagePart

    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, book_id: str) -> HTMLResponse:
        presenter = BookDetailPagePresenter(
            storage=self._books_storage, urls_manager=urls_manager
        )
        result = await presenter.present(book_id=book_id, part=self.part)
        return HTMLResponse.from_presenter_result(result)


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

    async def fire(self, book_id: str, clipping_id: str) -> HTMLResponse:
        presenter = ClippingPresenter(
            storage=self._books_storage, urls_manager=urls_manager
        )
        result = await presenter.present(book_id=book_id, clipping_id=clipping_id)
        return HTMLResponse.from_presenter_result(result)
