from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clippings.books.ports import BooksFinderABC, FinderQuery
from clippings.books.presenters.dtos import ActionDTO, PaginationItemDTO, UrlDTO
from clippings.books.presenters.urls import UrlsManager

if TYPE_CHECKING:
    from clippings.books.presenters.pagination import PaginationPresenter


@dataclass
class BookOnPageDTO:
    cover_url: str
    name: str
    clippings_count: int
    last_clipping_added_at: str
    rating: int
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


class BooksPagePresenter:
    def __init__(
        self,
        finder: BooksFinderABC,
        pagination_presenter: PaginationPresenter,
        urls_manager: UrlsManager,
    ) -> None:
        self._finder = finder
        self._pagination_presenter = pagination_presenter
        self._urls_manager = urls_manager

    async def present(self, page: int, on_page: int) -> BooksPageDTO:
        query = FinderQuery(start=(page - 1) * on_page, limit=on_page)
        books = await self._finder.find(query)
        books_count = await self._finder.count(FinderQuery(start=0, limit=None))
        books_url = self._urls_manager.build_url("book_list_page")
        return BooksPageDTO(
            page_title="Books",
            books=[
                BookOnPageDTO(
                    cover_url="https://placehold.co/400x600",
                    name=f"{book.title} by {book.author}",
                    clippings_count=len(book.clippings),
                    last_clipping_added_at="-",
                    rating=10,
                    review="",
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
            pagination=self._pagination_presenter(
                current_page=page,
                total_items=books_count,
                on_page=on_page,
                books_page_url=books_url.value,
            ),
        )
