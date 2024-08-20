from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clippings.books.presenters import jinja_env
from clippings.books.presenters.dtos import (
    ActionDTO,
    NotFoundDTO,
    UrlDTO,
    UrlTemplateDTO,
)

if TYPE_CHECKING:
    from clippings.books.ports import BooksStorageABC


@dataclass
class BookFieldDTO:
    label: str
    value: str


@dataclass
class BooksDetailDTO:
    page_title: str
    actions: list[ActionDTO]
    cover_url: str
    title: BookFieldDTO
    author: BookFieldDTO
    rating: BookFieldDTO
    review: BookFieldDTO
    count_of_clippings: BookFieldDTO

    @property
    def actions_map(self) -> dict[str, ActionDTO]:
        return {action.id: action for action in self.actions}


class BooksDetailPresenter:
    def __init__(self, storage: BooksStorageABC) -> None:
        self._storage = storage

    async def present(
        self,
        book_id: str,
        upload_cover_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/upload_cover", method="post"
        ),
        find_cover_url: UrlTemplateDTO = UrlTemplateDTO(
            template="/books/{book_id}/find_cover", method="post"
        ),
    ) -> BooksDetailDTO | NotFoundDTO:
        book = await self._storage.get(book_id)
        if book is None:
            return NotFoundDTO(
                page_title="Book not found",
                message="The book you are looking for does not exist.",
            )

        return BooksDetailDTO(
            page_title="Book detail",
            actions=[
                ActionDTO(
                    id="upload_cover",
                    label="Upload cover",
                    url=UrlDTO.from_template(upload_cover_url, book_id=book_id),
                ),
                ActionDTO(
                    id="find_cover",
                    label="Find cover",
                    url=UrlDTO.from_template(find_cover_url, book_id=book_id),
                ),
                ActionDTO(id="edit_review", label="Edit review", url=None),
            ],
            cover_url="https://placehold.co/400x600",
            title=BookFieldDTO(label="", value=book.title),
            author=BookFieldDTO(label="", value=f"by {book.author_name}"),
            rating=BookFieldDTO(label="Rating:", value="10/10"),
            review=BookFieldDTO(label="Review:", value="My review for this book"),
            count_of_clippings=BookFieldDTO(
                label="Clippings count:", value=str(len(book.clippings))
            ),
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
