import pytest

from clippings.books.use_cases.import_clippings import ImportedBookDTO
from clippings.web.presenters.book.clippings_import_page import (
    ImportClippingsResultPresenter,
)
from clippings.web.presenters.dtos import PresenterResult


@pytest.fixture()
def make_sut():
    def _make_sut():
        return ImportClippingsResultPresenter()

    return _make_sut


async def test_present_with_non_empty_statistics(make_sut):
    sut = make_sut()
    statistics = [
        ImportedBookDTO(
            title="Book 1", authors="Author 1", imported_clippings_count=3, is_new=True
        ),
        ImportedBookDTO(
            title="Book 2", authors="Author 2", imported_clippings_count=5, is_new=False
        ),
    ]

    result = await sut.present(statistics)

    assert isinstance(result, PresenterResult)
    assert result.data.is_empty is False
    assert len(result.data.items) == 2
    first_book, second_book = result.data.items
    assert first_book.book_name == "Book 1 by Author 1"
    assert second_book.book_name == "Book 2 by Author 2"
    assert first_book.new_label
    assert second_book.new_label is None
    assert isinstance(result.render(), str)


async def test_present_with_empty_statistics(make_sut):
    # Arrange
    sut = make_sut()
    statistics = []

    # Act
    result: PresenterResult = await sut.present(statistics)

    # Assert
    assert isinstance(result, PresenterResult)
    assert result.data.is_empty is True
    assert result.data.empty_message
    assert result.data.items == []
    assert isinstance(result.render(), str)
