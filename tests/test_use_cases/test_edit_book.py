from unittest.mock import create_autospec

import pytest

from clippings.books.ports import BooksStorageABC
from clippings.books.use_cases.edit_book import (
    EditBookUseCase,
    RatingDTO,
    ReviewDTO,
    TitleDTO,
)
from clippings.seedwork.exceptions import DomainError


@pytest.fixture()
def make_sut(memory_book_storage, enrich_books_meta_service):
    def _make_sut(books_storage=memory_book_storage):
        return EditBookUseCase(
            book_storage=books_storage,
            enrich_books_meta_service=enrich_books_meta_service,
        )

    return _make_sut


async def test_update_book_with_title_and_authors(
    make_sut, memory_book_storage, mother
):
    # Arrange
    book = mother.book(id="book-id", title="Old Title", authors=["Old Author"])
    await memory_book_storage.add(book)
    sut = make_sut()
    fields = [TitleDTO(title="New Title", authors="New Author")]

    # Act
    result = await sut.execute("book-id", fields)

    # Assert
    assert result is None
    updated_book = await memory_book_storage.get("book-id")
    assert updated_book.title == "New Title"
    assert updated_book.authors_to_str() == "New Author"


@pytest.mark.parametrize(
    "new_title,new_author",
    [
        ("New Title", "Old Author"),
        ("Old Title", "New Author"),
        ("New Title", "New Author"),
    ],
)
async def test_update_book_with_title_or_authors_set_cover(
    new_title, new_author, make_sut, memory_book_storage, mother
):
    # Arrange
    book = mother.book(
        id="book-id", title="Old Title", authors=["Old Author"], meta=None
    )
    await memory_book_storage.add(book)
    sut = make_sut()
    fields = [TitleDTO(title=new_title, authors=new_author)]

    # Act
    result = await sut.execute("book-id", fields)

    # Assert
    assert result is None
    updated_book = await memory_book_storage.get("book-id")
    assert updated_book.meta is not None


@pytest.mark.parametrize("new_rating", [9, None])
async def test_update_book_rating(make_sut, memory_book_storage, mother, new_rating):
    # Arrange
    book = mother.book(id="book-id", rating=3)
    await memory_book_storage.add(book)
    sut = make_sut()
    fields = [RatingDTO(rating=new_rating)]

    # Act
    result = await sut.execute("book-id", fields)

    # Assert
    assert result is None
    updated_book = await memory_book_storage.get("book-id")
    assert updated_book.rating == new_rating


async def test_update_book_review(make_sut, memory_book_storage, mother):
    # Arrange
    book = mother.book(id="book-id", review="Old Review")
    await memory_book_storage.add(book)
    sut = make_sut()
    fields = [ReviewDTO(review="New Review")]

    # Act
    result = await sut.execute("book-id", fields)

    # Assert
    assert result is None
    updated_book = await memory_book_storage.get("book-id")
    assert updated_book.review == "New Review"


async def test_do_not_update_when_no_fields_change(make_sut, mother):
    # Arrange
    book = mother.book(
        id="book-id",
        title="Test Title",
        authors=["Author 1"],
        review="Test Review",
        rating=5,
    )
    book_storage = create_autospec(BooksStorageABC, instance=True)
    book_storage.get.return_value = book
    sut = make_sut(book_storage)
    fields = [
        TitleDTO(title="Test Title", authors="Author 1"),
        RatingDTO(rating=5),
        ReviewDTO(review="Test Review"),
    ]

    # Act
    result = await sut.execute("book-id", fields)

    # Assert
    assert result is None
    book_storage.get.assert_awaited_once_with("book-id")
    book_storage.add.assert_not_awaited()


async def test_return_error_when_book_not_found(make_sut, memory_book_storage, mother):
    # Arrange
    book = mother.book(id="book-id")
    await memory_book_storage.add(book)
    sut = make_sut()
    fields = []

    # Act
    result = await sut.execute("unknown-book-id", fields)

    # Assert
    assert isinstance(result, DomainError)
    assert str(result) == "Can't find book with id: unknown-book-id"
