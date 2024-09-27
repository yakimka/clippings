from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clippings.books.adapters.storages import (
    MockDeletedHashStorage,
    MongoDeletedHashStorage,
)

if TYPE_CHECKING:
    from clippings.books.ports import DeletedHashStorageABC


@pytest.fixture(params=["mock", "mongo"])
def make_sut(request, mongo_db):
    async def _make_sut() -> DeletedHashStorageABC:
        if request.param == "mock":
            storage = MockDeletedHashStorage()
        elif request.param == "mongo":
            storage = MongoDeletedHashStorage(mongo_db, user_id="user_id")
        else:
            raise ValueError(f"Unknown storage type: {request.param}")
        return storage

    return _make_sut


async def test_get_all_empty(make_sut):
    sut = await make_sut()

    result = await sut.get_all()

    assert result == []


async def test_add_and_get_hash(make_sut, mother):
    sut = await make_sut()
    deleted_hash = mother.deleted_hash(id="deleted_hash:id")

    await sut.add(deleted_hash)

    result = await sut.get_all()

    assert result == [deleted_hash]
