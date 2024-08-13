from __future__ import annotations

import abc
from dataclasses import dataclass

from jinja2 import Template

from clippings.books.ports import BooksFinderABC, FinderQuery
from clippings.books.presenters import TEMPLATES_DIR
from clippings.books.presenters.dtos import ButtonDTO, PaginationItemDTO


@dataclass
class BookOnPageDTO:
    book_id: str
    cover_url: str
    title: str
    author: str
    clippings_count: int
    last_clipping_added_at: str
    rating: int
    review: str


@dataclass
class BooksPageDTO:
    page_title: str
    books: list[BookOnPageDTO]
    page: int
    total_pages: int
    import_button: ButtonDTO
    add_book_button: ButtonDTO
    headers: list[str]
    pages: list[PaginationItemDTO]


class BooksPagePresenter:
    def __init__(self, finder: BooksFinderABC) -> None:
        self._finder = finder

    async def present(
        self,
        page: int,
        on_page: int,
    ) -> BooksPageDTO:
        query = FinderQuery(start=(page - 1) * on_page, limit=on_page)
        books = await self._finder.find(query)
        books_count = await self._finder.count(FinderQuery(start=0, limit=None))
        books_dto = []
        for book in books:
            books_dto.append(
                BookOnPageDTO(
                    book_id=book.id,
                    cover_url="https://placehold.co/400x600",
                    title=book.title,
                    author=book.author.name,
                    clippings_count=len(book.clippings),
                    last_clipping_added_at="-",
                    rating=10,
                    review="",
                )
            )

        return BooksPageDTO(
            page_title="Books",
            books=books_dto,
            page=page,
            total_pages=(books_count + on_page - 1) // on_page,
            import_button=ButtonDTO(
                label="Import",
                url="/import",
            ),
            add_book_button=ButtonDTO(
                label="Add book",
                url="/add",
            ),
            headers=[
                "Cover",
                "Book",
                "Clippings count",
                "Last added",
                "Rating",
                "Review",
                "Actions",
            ],
            pages=[
                PaginationItemDTO(
                    number=i,
                    current=i == 1,
                    url=f"/books?page={i}",
                )
                for i in range(1, 10)
            ],
        )


class BooksPageStringRenderedABC(abc.ABC):
    @abc.abstractmethod
    async def render(self, dto: BooksPageDTO) -> str:
        pass


class BooksPageHtmlRendered(BooksPageStringRenderedABC):
    def __init__(self) -> None:
        self._template = (TEMPLATES_DIR / "books_page.html").read_text()

    async def render(self, dto: BooksPageDTO) -> str:
        template = Template(self._template)
        return template.render(data=dto)
