from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clippings.web.presenters.dtos import ActionDTO, PaginationItemDTO, PresenterResult
from clippings.web.presenters.html_renderers import make_html_renderer
from clippings.web.presenters.image import image_or_default

if TYPE_CHECKING:
    from clippings.books.entities import Clipping
    from clippings.books.ports import BooksStorageABC
    from clippings.web.presenters.pagination import PaginationCalculator
    from clippings.web.presenters.urls import UrlsManager


@dataclass
class BookOnPageDTO:
    cover_url: str
    name: str
    clippings_count: int
    last_clipping_added_at: str
    rating: str
    actions: list[ActionDTO]

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}


@dataclass
class BooksPageDTO:
    page_title: str
    books: list[BookOnPageDTO]
    fields_meta: dict[str, dict[str, str]]
    pagination: list[PaginationItemDTO]


class BooksListPagePresenter:
    def __init__(
        self,
        storage: BooksStorageABC,
        pagination_calculator: PaginationCalculator,
        urls_manager: UrlsManager,
    ) -> None:
        self._storage = storage
        self._pagination_calculator = pagination_calculator
        self._urls_manager = urls_manager

    async def present(self, page: int, on_page: int) -> PresenterResult[BooksPageDTO]:
        books_count = await self._storage.count(
            self._storage.FindQuery(start=0, limit=None)
        )
        books_url = self._urls_manager.build_url("book_list_page")
        pagination = self._pagination_calculator(
            current_page=page,
            total_items=books_count,
            on_page=on_page,
            books_page_url=books_url.value,
        )
        page = pagination.current_page

        query = self._storage.FindQuery(start=(page - 1) * on_page, limit=on_page)
        books = await self._storage.find(query)

        def last_clipping_date(clippings: list[Clipping]) -> str:
            if not clippings:
                return "-"
            last_clipping = sorted(clippings, key=lambda c: c.added_at)[-1]
            return last_clipping.added_at.strftime("%d %b %Y")

        data = BooksPageDTO(
            page_title="Books",
            books=[
                BookOnPageDTO(
                    cover_url=image_or_default(book.cover_url),
                    name=f"{book.title} by {book.authors[0]}",
                    clippings_count=len(book.clippings),
                    last_clipping_added_at=last_clipping_date(book.clippings),
                    rating="-" if book.rating is None else str(book.rating),
                    actions=[
                        ActionDTO(
                            id="book_detail_page",
                            label="View",
                            url=self._urls_manager.build_url(
                                "book_detail_page", book_id=book.id
                            ),
                        ),
                        ActionDTO(
                            id="book_delete",
                            label="Delete",
                            confirm_message=(
                                f"Are you sure you want to delete {book.title}?"
                            ),
                            url=self._urls_manager.build_url(
                                "book_delete", book_id=book.id
                            ),
                        ),
                    ],
                )
                for book in books
            ],
            fields_meta={
                "cover_url": {"label": "Cover"},
                "name": {"label": "Book"},
                "clippings_count": {"label": "Clippings count"},
                "last_clipping_added_at": {"label": "Last added"},
                "rating": {"label": "Rating"},
                "actions": {"label": "Actions"},
            },
            pagination=pagination.items,
        )
        return PresenterResult(
            data=data,
            renderer=make_html_renderer("book/list_page.jinja2"),
        )
