from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING

from jinja2 import Template

from clippings.books.presenters import TEMPLATES_DIR
from clippings.books.presenters.dtos import ButtonDTO, NotFoundDTO

if TYPE_CHECKING:
    from clippings.books.ports import BooksStorageABC


@dataclass
class BooksDetailDTO:
    page_title: str
    upload_cover_button: ButtonDTO
    find_cover_button: ButtonDTO
    edit_review_button: ButtonDTO
    book_cover_url: str
    book_title: str
    book_author: str
    book_rating: int
    book_review: str
    count_of_clippings: int


class BooksDetailPresenter:
    def __init__(self, storage: BooksStorageABC) -> None:
        self._storage = storage

    async def present(self, book_id: str) -> BooksDetailDTO | NotFoundDTO:
        book = await self._storage.get(book_id)
        if book is None:
            return NotFoundDTO(
                page_title="Book not found",
                message="The book you are looking for does not exist.",
            )

        return BooksDetailDTO(
            page_title="Book detail",
            upload_cover_button=ButtonDTO(label="Upload cover", url="/"),
            find_cover_button=ButtonDTO(label="Find cover", url="/"),
            edit_review_button=ButtonDTO(label="Edit review", url="/"),
            book_cover_url="https://placehold.co/400x600",
            book_title=book.title,
            book_author=book.author_name,
            book_rating=10,
            book_review="My review for this book",
            count_of_clippings=len(book.clippings),
        )


class BooksDetailStringRenderedABC(abc.ABC):
    @abc.abstractmethod
    async def render(self, dto: BooksDetailDTO | NotFoundDTO) -> str:
        pass


class BooksDetailHtmlRendered(BooksDetailStringRenderedABC):
    def __init__(self) -> None:
        self._template = (TEMPLATES_DIR / "books_detail.html").read_text()

    async def render(self, dto: BooksDetailDTO | NotFoundDTO) -> str:
        template = Template(self._template)
        return template.render(data=dto)
