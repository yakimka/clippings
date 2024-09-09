from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clippings.books.ports import BooksFinderABC, FinderQuery
from clippings.books.presenters.dtos import (
    ActionDTO,
    PaginationItemDTO,
    PresenterResult,
)
from clippings.books.presenters.html_renderers import make_html_renderer
from clippings.books.presenters.image import image_or_default

if TYPE_CHECKING:
    from clippings.books.entities import Clipping
    from clippings.books.presenters.pagination import PaginationCalculator
    from clippings.books.presenters.urls import UrlsManager


@dataclass
class BookOnPageDTO:
    cover_url: str
    name: str
    clippings_count: int
    last_clipping_added_at: str
    rating: str
    review: str
    actions: list[ActionDTO]

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}


@dataclass
class BooksPageDTO:
    page_title: str
    books: list[BookOnPageDTO]
    actions: list[ActionDTO]
    fields_meta: dict[str, dict[str, str]]
    pagination: list[PaginationItemDTO]

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}


class BooksListPagePresenter:
    def __init__(
        self,
        finder: BooksFinderABC,
        pagination_calculator: PaginationCalculator,
        urls_manager: UrlsManager,
        html_template: str = "books_list_page.jinja2",
    ) -> None:
        self._finder = finder
        self._pagination_calculator = pagination_calculator
        self._urls_manager = urls_manager
        self._renderer = make_html_renderer(html_template)

    async def present(self, page: int, on_page: int) -> PresenterResult[BooksPageDTO]:
        books_count = await self._finder.count(FinderQuery(start=0, limit=None))
        books_url = self._urls_manager.build_url("book_list_page")
        pagination = self._pagination_calculator(
            current_page=page,
            total_items=books_count,
            on_page=on_page,
            books_page_url=books_url.value,
        )
        page = pagination.current_page

        query = FinderQuery(start=(page - 1) * on_page, limit=on_page)
        books = await self._finder.find(query)

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
                    name=f"{book.title} by {book.author}",
                    clippings_count=len(book.clippings),
                    last_clipping_added_at=last_clipping_date(book.clippings),
                    rating="-" if book.rating is None else str(book.rating),
                    review=sub_by_words(book.review, 100),
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
                            url=self._urls_manager.build_url(
                                "book_delete", book_id=book.id
                            ),
                        ),
                    ],
                )
                for book in books
            ],
            actions=[
                ActionDTO(
                    id="import_clippings",
                    label="Import",
                    url=self._urls_manager.build_url("clipping_import_page"),
                )
            ],
            fields_meta={
                "cover_url": {"label": "Cover"},
                "name": {"label": "Book"},
                "clippings_count": {"label": "Clippings count"},
                "last_clipping_added_at": {"label": "Last added"},
                "rating": {"label": "Rating"},
                "review": {"label": "Review"},
                "actions": {"label": "Actions"},
            },
            pagination=pagination.items,
        )
        return PresenterResult(
            data=data,
            renderer=self._renderer,
        )


def sub_by_words(text: str, max_length: int) -> str:
    words = text.split()
    result: list[str] = []
    for word in words:
        if len(result) + len(word) > max_length:
            result.append("...")
            break
        result.append(word)
    return " ".join(result)