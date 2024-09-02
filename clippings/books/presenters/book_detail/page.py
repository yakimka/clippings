from __future__ import annotations

from enum import Enum

from clippings.books.ports import BooksStorageABC
from clippings.books.presenters.book_detail.builders import BookDetailBuilder
from clippings.books.presenters.book_detail.dtos import BookDetailDTO, ClippingDTO
from clippings.books.presenters.dtos import NotFoundPresenterResult, PresenterResult
from clippings.books.presenters.html_renderers import make_html_renderer
from clippings.books.presenters.urls import UrlsManager


class BookDetailPagePart(Enum):
    ALL = "book_detail/page.jinja2"
    INFO = "book_detail/info.jinja2"
    REVIEW = "book_detail/review.jinja2"
    CLIPPINGS = "book_detail/clippings.jinja2"


class BookDetailPagePresenter:
    def __init__(
        self,
        storage: BooksStorageABC,
        urls_manager: UrlsManager,
    ) -> None:
        self._storage = storage
        self._urls_manager = urls_manager

    async def present(
        self, book_id: str, part: BookDetailPagePart = BookDetailPagePart.ALL
    ) -> PresenterResult[BookDetailDTO] | NotFoundPresenterResult:
        book = await self._storage.get(book_id)
        if book is None:
            return PresenterResult.not_found()
        builder = BookDetailBuilder(book, self._urls_manager)

        return PresenterResult(
            data=builder.detail_dto(), renderer=make_html_renderer(part.value)
        )


class ClippingPart(Enum):
    ALL = "book_detail/clipping.jinja2"


class ClippingPresenter:
    def __init__(
        self,
        storage: BooksStorageABC,
        urls_manager: UrlsManager,
    ) -> None:
        self._storage = storage
        self._urls_manager = urls_manager

    async def present(
        self, book_id: str, clipping_id: str, part: ClippingPart = ClippingPart.ALL
    ) -> PresenterResult[ClippingDTO] | NotFoundPresenterResult:
        book = await self._storage.get(book_id)
        if book is None:
            return PresenterResult.not_found()
        clipping = book.get_clipping(clipping_id)
        if clipping is None:
            return PresenterResult.not_found()
        builder = BookDetailBuilder(book, self._urls_manager)

        return PresenterResult(
            data=builder.clipping_dto(clipping_id),
            renderer=make_html_renderer(part.value),
        )
