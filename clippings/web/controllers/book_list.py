from __future__ import annotations

from typing import TYPE_CHECKING

from picodi import Provide, inject

from clippings.deps import get_books_storage
from clippings.web.controllers.responses import HTMLResponse
from clippings.web.presenters.book.list_page import BooksListPagePresenter
from clippings.web.presenters.pagination import classic_pagination_calculator
from clippings.web.presenters.urls import urls_manager

if TYPE_CHECKING:
    from clippings.books.ports import BooksStorageABC


class RenderBookListController:
    @inject
    def __init__(
        self,
        books_storage: BooksStorageABC = Provide(get_books_storage),
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, page: int, on_page: int) -> HTMLResponse:
        presenter = BooksListPagePresenter(
            storage=self._books_storage,
            pagination_calculator=classic_pagination_calculator,
            urls_manager=urls_manager,
        )
        result = await presenter.present(page=page, on_page=on_page)
        return HTMLResponse.from_presenter_result(result)
