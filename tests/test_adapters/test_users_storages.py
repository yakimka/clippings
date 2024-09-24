from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clippings.users.adapters.storages import MockUsersStorage

if TYPE_CHECKING:
    from clippings.users.entities import User
    from clippings.users.ports import UsersStorageABC


@pytest.fixture(params=["mock"])
def make_sut(request):
    async def _make_sut(users: list[User] | None = None) -> UsersStorageABC:
        if request.param == "mock":
            storage = MockUsersStorage()
        else:
            raise ValueError(f"Unknown storage type: {request.param}")
        if users is not None:
            for user in users:
                await storage.add(user)
        return storage

    return _make_sut


async def test_get_user_by_id(make_sut, mother):
    user = mother.user(id="1", nickname="It' me Mario")
    storage = await make_sut([user])

    result = await storage.get("1")

    assert result == user


async def test_get_user_by_id_not_found(make_sut, mother):
    user = mother.user(id="2", nickname="It' me Mario")
    storage = await make_sut([user])

    result = await storage.get("1")

    assert result is None


async def test_get_user_by_nickname(make_sut, mother):
    user = mother.user(id="1", nickname="It' me Mario")
    storage = await make_sut([user])

    result = await storage.get_by_nickname("It' me Mario")

    assert result == user


async def test_get_user_by_nickname_not_found(make_sut, mother):
    user = mother.user(id="1", nickname="It' me Luigi")
    storage = await make_sut([user])

    result = await storage.get_by_nickname("It' me Mario")

    assert result is None


async def test_add_user(make_sut, mother):
    user = mother.user(id="1", nickname="It' me Mario")
    storage = await make_sut()

    await storage.add(user)

    assert await storage.get("1") == user


async def test_users_is_unique_by_id(make_sut, mother):
    luigi = mother.user(id="1", nickname="It' me Luigi")
    mario = mother.user(id="1", nickname="It' me Mario")
    storage = await make_sut()
    await storage.add(luigi)
    await storage.add(mario)

    result = await storage.get("1")

    assert result == mario
