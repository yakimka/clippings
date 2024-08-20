from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clippings.books.ports import BooksFinderABC, FinderQuery
from clippings.books.presenters import jinja_env
from clippings.books.presenters.dtos import (
    ActionDTO,
    PaginationItemDTO,
    UrlDTO,
    UrlTemplateDTO,
)

if TYPE_CHECKING:
    from clippings.books.presenters.pagination_presenter import PaginationPresenter


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
    field_labels: list[tuple[str, str]]
    pagination: list[PaginationItemDTO]

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}


class BooksPagePresenter:
    def __init__(
        self, finder: BooksFinderABC, pagination_presenter: PaginationPresenter
    ) -> None:
        self._finder = finder
        self._pagination_presenter = pagination_presenter

    async def present(
        self,
        page: int,
        on_page: int,
        books_url: str = "/books",
        view_book_url: UrlTemplateDTO = UrlTemplateDTO(template="/books/{book_id}"),
        delete_book_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}", method="delete"
        ),
        import_clippings_url: UrlTemplateDTO = UrlTemplateDTO(template="/books/import"),
        add_book_url: UrlTemplateDTO = UrlTemplateDTO(template="/books/add"),
    ) -> BooksPageDTO:
        query = FinderQuery(start=(page - 1) * on_page, limit=on_page)
        books = await self._finder.find(query)
        books_count = await self._finder.count(FinderQuery(start=0, limit=None))
        return BooksPageDTO(
            page_title="Books",
            books=[
                BookOnPageDTO(
                    cover_url="https://placehold.co/400x600",
                    name=f"{book.title} by {book.author_name}",
                    clippings_count=len(book.clippings),
                    last_clipping_added_at="-",
                    rating=10,
                    review="",
                    actions=[
                        ActionDTO(
                            id="view_book",
                            label="View",
                            url=UrlDTO.from_template(view_book_url, book_id=book.id),
                        ),
                        ActionDTO(
                            id="delete_book",
                            label="Delete",
                            url=UrlDTO.from_template(delete_book_url, book_id=book.id),
                        ),
                    ],
                )
                for book in books
            ],
            actions=[
                ActionDTO(
                    id="import_clippings",
                    label="Import",
                    url=UrlDTO.from_template(import_clippings_url),
                ),
                ActionDTO(
                    id="add_book",
                    label="Add book",
                    url=UrlDTO.from_template(add_book_url),
                ),
            ],
            field_labels=[
                ("cover_url", "Cover"),
                ("name", "Book"),
                ("clippings_count", "Clippings count"),
                ("last_clipping_added_at", "Last added"),
                ("rating", "Rating"),
                ("review", "Review"),
                ("actions", "Actions"),
            ],
            pagination=self._pagination_presenter(
                current_page=page,
                total_items=books_count,
                on_page=on_page,
                books_page_url=books_url,
            ),
        )


class BooksPageStringRenderedABC(abc.ABC):
    @abc.abstractmethod
    async def render(self, dto: BooksPageDTO) -> str:
        pass


class BooksPageHtmlRendered(BooksPageStringRenderedABC):
    def __init__(self) -> None:
        self._template_name = "books_page.jinja2"
        self._env = jinja_env

    async def render(self, dto: BooksPageDTO) -> str:
        return self._env.get_template(self._template_name).render(data=dto)
