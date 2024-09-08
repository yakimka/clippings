from picodi import Provide, inject

from clippings.books.ports import BooksFinderABC
from clippings.web.deps import get_books_finder
from clippings.web.presenters.book.list_page import BooksListPagePresenter
from clippings.web.presenters.dtos import PresenterResult
from clippings.web.presenters.pagination import classic_pagination_calculator
from clippings.web.presenters.urls import urls_manager


class RenderBookListController:
    @inject
    def __init__(
        self,
        book_finder: BooksFinderABC = Provide(get_books_finder),
    ) -> None:
        self._book_finder = book_finder

    async def fire(self, page: int, on_page: int) -> PresenterResult:
        presenter = BooksListPagePresenter(
            finder=self._book_finder,
            pagination_calculator=classic_pagination_calculator,
            urls_manager=urls_manager,
        )
        return await presenter.present(page=page, on_page=on_page)
