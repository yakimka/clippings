from __future__ import annotations

from typing import TYPE_CHECKING

from clippings.users.ports import UsersStorageABC

if TYPE_CHECKING:
    from clippings.users.entities import User


class MockUsersStorage(UsersStorageABC):
    def __init__(self, users_map: dict[str, User] | None = None) -> None:
        self.users: dict[str, User] = {} if users_map is None else users_map

    async def get(self, id: str) -> User | None:
        return self.users.get(id)

    async def get_by_nickname(self, nickname: str) -> User | None:
        for user in self.users.values():
            if user.nickname == nickname:
                return user
        return None

    async def add(self, user: User) -> None:
        self.users[user.id] = user
