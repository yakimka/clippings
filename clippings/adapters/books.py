from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Template

from clippings.domain.books import (
    Book,
    BookOnPageDTO,
    BooksFinderABC,
    BooksPageDTO,
    BooksPageHtmlRenderedABC,
    BooksPresenterABC,
    BooksStorage,
    ButtonDTO,
    ClippingImportCandidateDTO,
    ClippingsReader,
    FinderQuery,
    SelectDTO,
    SelectOptionDTO,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


class MockClippingsReader(ClippingsReader):
    def __init__(self, clippings: list[ClippingImportCandidateDTO]) -> None:
        self._clippings = clippings

    async def read(self) -> AsyncGenerator[ClippingImportCandidateDTO, None]:
        for clipping in self._clippings:
            yield clipping


class MockBooksStorage(BooksStorage):
    def __init__(self) -> None:
        self._books: dict[str, Book] = {}

    async def get(self, id: str) -> Book | None:
        return self._books.get(id)

    async def add(self, book: Book) -> None:
        self._books[book.id] = book

    async def extend(self, books: list[Book]) -> None:
        for book in books:
            await self.add(book)


_default_query = FinderQuery()


class MockBooksFinder(BooksFinderABC):
    def __init__(self, books_map: dict[str, Book] | None = None) -> None:
        self._books: dict[str, Book] = {} if books_map is None else books_map

    async def find(self, query: FinderQuery = _default_query) -> list[Book]:
        books = sorted(self._books.values(), key=lambda b: (b.title, b.id))
        start = query.start
        if query.limit is None:
            return books[start:]
        end = start + query.limit
        return books[start:end]

    async def count(self, query: FinderQuery = _default_query) -> int:  # noqa: U100
        return len(await self.find(FinderQuery(start=0, limit=None)))


class BooksPresenter(BooksPresenterABC):
    def __init__(self, finder: BooksFinderABC) -> None:
        self._finder = finder

    async def for_page(
        self,
        page: int,
        on_page: int,
    ) -> BooksPageDTO:
        query = FinderQuery(start=(page - 1) * on_page, limit=on_page)
        books = await self._finder.find(query)
        books_count = await self._finder.count(query)
        books_dto = []
        for book in books:
            books_dto.append(
                BookOnPageDTO(
                    book_id=book.id,
                    cover_url="https://example.com/cover.jpg",
                    title=book.title,
                    author=book.author.name,
                    clippings_count=len(book.clippings),
                    last_clipping_added_at="-",
                    rating=10,
                    review="",
                )
            )

        return BooksPageDTO(
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
            sort_select=SelectDTO(
                label="Sort by",
                options=[
                    SelectOptionDTO(label="Title", value="title"),
                    SelectOptionDTO(label="Author", value="author"),
                    SelectOptionDTO(label="Rating", value="rating"),
                    SelectOptionDTO(label="Clippings count", value="clippings_count"),
                ],
            ),
        )


class BooksPageHtmlRendered(BooksPageHtmlRenderedABC):
    def __init__(self) -> None:
        base_path = Path(__file__).parent
        self._template = (base_path / "books_page.html").read_text()

    async def render(self, dto: BooksPageDTO) -> str:
        template = Template(self._template)
        return template.render(data=dto)
