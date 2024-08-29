from __future__ import annotations

from clippings.books.ports import BooksStorageABC
from clippings.books.presenters.book_detail.builders import BookDetailBuilder
from clippings.books.presenters.book_detail.dtos import (
    BookDetailDTO,
    BookEditInfoDTO,
    BookInfoDTO,
    BookReviewDTO,
)
from clippings.books.presenters.dtos import ActionDTO
from clippings.books.presenters.urls import UrlsManager


class BookDetailPresenter:
    def __init__(self, storage: BooksStorageABC, urls_manager: UrlsManager) -> None:
        self._storage = storage
        self._urls_manager = urls_manager

    async def _retrieve_builder(self, book_id: str) -> BookDetailBuilder | None:
        book = await self._storage.get(book_id)
        if book is None:
            return None
        return BookDetailBuilder(book, self._urls_manager)

    async def page(self, book_id: str) -> BookDetailDTO | None:
        builder = await self._retrieve_builder(book_id)
        if builder is None:
            return None

        return builder.detail_dto()

    async def book_info(self, book_id: str) -> BookInfoDTO | None:
        builder = await self._retrieve_builder(book_id)
        if builder is None:
            return None

        return builder.main_info_dto()

    async def edit_book_info(self, book_id: str) -> BookEditInfoDTO | None:
        book = await self._storage.get(book_id)
        if book is None:
            return None

        builder = BookDetailBuilder(book, self._urls_manager)
        main_info_dto = builder.main_info_dto()
        return BookEditInfoDTO(
            cover_url=main_info_dto.cover_url,
            title=book.title,
            author=book.author,
            rating=str(book.rating),
            fields_meta={
                "title": {"label": "Book Title"},
                "author": {"label": "Author"},
                "rating": {"label": "Rating", "min": 0, "max": 10},
                "cover": {"label": "Upload cover"},
            },
            actions=[
                ActionDTO(
                    id="save",
                    label="Save",
                    url=self._urls_manager.build_url(
                        "book_info_update", book_id=book_id
                    ),
                ),
                ActionDTO(
                    id="cancel",
                    label="Cancel",
                    url=self._urls_manager.build_url("book_info", book_id=book_id),
                ),
            ],
        )

    async def review(self, book_id: str) -> BookReviewDTO | None:
        builder = await self._retrieve_builder(book_id)
        if builder is None:
            return None

        return builder.review_dto()

    async def edit_review(self, book_id: str) -> BookReviewDTO | None:
        book = await self._storage.get(book_id)
        if book is None:
            return None

        return BookReviewDTO(
            review=book.review,
            actions=[
                ActionDTO(
                    id="save",
                    label="Save",
                    url=self._urls_manager.build_url(
                        "book_review_update", book_id=book_id
                    ),
                ),
                ActionDTO(
                    id="cancel",
                    label="Cancel",
                    url=self._urls_manager.build_url("book_review", book_id=book_id),
                ),
            ],
        )
