from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from clippings.books.use_cases.restore_data import RestoreDataUseCase
from clippings.seedwork.exceptions import DomainError

if TYPE_CHECKING:
    from io import BytesIO


@pytest.fixture()
def make_sut(mock_book_storage, mock_deleted_hash_storage):
    def _make_sut():
        return RestoreDataUseCase(
            mock_book_storage, deleted_hash_storage=mock_deleted_hash_storage
        )

    return _make_sut


@pytest.fixture()
def backup() -> BytesIO:
    this_dir = Path(__file__).parent
    with open(this_dir / "my-clippings-backup.ndjson", "rb") as fp:
        yield fp


async def test_can_restore_data(make_sut, backup):
    sut = make_sut()

    result = await sut.execute(backup)

    assert not isinstance(result, DomainError)
