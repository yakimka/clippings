import pytest

from clippings.books.use_cases.edit_book import ClearDeletedHashesUseCase


@pytest.fixture()
def make_sut(memory_deleted_hash_storage):
    def _make_sut():
        return ClearDeletedHashesUseCase(memory_deleted_hash_storage)

    return _make_sut


async def test_successfully_clear_deleted_hashes(
    make_sut, memory_deleted_hash_storage, mother
):
    await memory_deleted_hash_storage.add(mother.deleted_hash())
    sut = make_sut()

    await sut.execute()

    assert await memory_deleted_hash_storage.get_all() == []
