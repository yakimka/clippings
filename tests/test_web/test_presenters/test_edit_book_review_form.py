from unittest.mock import AsyncMock

import pytest

from clippings.web.presenters.book.detail.forms import (
    EditBookReviewDTO,
    EditBookReviewFormPresenter,
)
from clippings.web.presenters.book.system_pages import NotFoundDTO
from clippings.web.presenters.urls import urls_manager


@pytest.fixture()
def make_sut(memory_book_storage):
    def _make_sut(book_storage=memory_book_storage):
        return EditBookReviewFormPresenter(
            storage=book_storage, urls_manager=urls_manager
        )

    return _make_sut


async def test_present_should_return_edit_book_review_dto_when_book_is_found(
    make_sut, memory_book_storage, mother
):
    sut = make_sut()
    book = mother.book(id="book-id", review="Sample Book Review")
    await memory_book_storage.add(book)

    result = await sut.present(book_id="book-id")

    assert isinstance(result.data, EditBookReviewDTO)
    assert result.data.review == "Sample Book Review"
    assert result.data.actions
    assert isinstance(result.render(), str)


async def test_present_should_return_not_found_when_book_is_not_found(
    make_sut, memory_book_storage
):
    sut = make_sut()
    memory_book_storage.get = AsyncMock(return_value=None)

    result = await sut.present(book_id="book-id")

    assert isinstance(result.data, NotFoundDTO)
    assert isinstance(result.render(), str)
