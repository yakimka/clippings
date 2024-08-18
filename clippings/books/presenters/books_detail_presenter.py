from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clippings.books.presenters import jinja_env
from clippings.books.presenters.dtos import ActionDTO, NotFoundDTO

if TYPE_CHECKING:
    from clippings.books.ports import BooksStorageABC


@dataclass
class BooksDetailDTO:
    page_title: str
    upload_cover_button: ActionDTO
    find_cover_button: ActionDTO
    edit_review_button: ActionDTO
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
            upload_cover_button=ActionDTO(label="Upload cover", url="/"),
            find_cover_button=ActionDTO(label="Find cover", url="/"),
            edit_review_button=ActionDTO(label="Edit review", url="/"),
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
        self._template_name = "books_detail.jinja2"
        self._env = jinja_env

    async def render(self, dto: BooksDetailDTO | NotFoundDTO) -> str:
        return self._env.get_template(self._template_name).render(data=dto)
