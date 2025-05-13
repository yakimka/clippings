from __future__ import annotations

import io
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from clippings.books.use_cases.restore_data import RestoreDataUseCase
from clippings.seedwork.exceptions import DomainError

if TYPE_CHECKING:
    from io import BytesIO


pytestmark = pytest.mark.usefixtures("user")


@pytest.fixture()
def make_sut(
    mock_book_storage,
    mock_deleted_hash_storage,
    enrich_books_meta_service,
    mock_users_storage,
):
    def _make_sut():
        return RestoreDataUseCase(
            mock_book_storage,
            deleted_hash_storage=mock_deleted_hash_storage,
            enrich_books_meta_service=enrich_books_meta_service,
            users_storage=mock_users_storage,
        )

    return _make_sut


@pytest.fixture()
def backup() -> BytesIO:
    this_dir = Path(__file__).parent
    with open(this_dir / "my-clippings-backup.ndjson", "rb") as fp:
        yield fp


async def test_can_restore_data(make_sut, backup):
    sut = make_sut()

    result = await sut.execute(backup, user_id="user:42")

    assert not isinstance(result, DomainError)


@pytest.mark.parametrize(
    "data,error_substring",
    [
        ('{"type": "book", "title": "Book 1"}', "'book' is not one of"),
        (
            (
                '{"type": "book", "id": "3HO80FBBAA3DB", "title": "Title", "authors": '
                '["Author"], "review": "", "rating": null, "clippings": '
                '[{"id": "2KCT2A45XNHCI", "page": [44, 44]}]}'
            ),
            "is not valid under any of the given schemas",
        ),
        ("{", "Invalid JSON at line 2"),
    ],
)
async def test_cant_restore_data_with_invalid_data(data, error_substring, make_sut):
    sut = make_sut()
    text_data = f'{{"version": "1"}}\n{data}'

    result = await sut.execute(io.BytesIO(text_data.encode("utf-8")), user_id="user:42")

    assert isinstance(result, DomainError)
    assert error_substring in str(result)
