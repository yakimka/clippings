from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from dacite import from_dict

from clippings.users.entities import User
from clippings.users.ports import UsersStorageABC

if TYPE_CHECKING:
    from collections.abc import Callable

    from motor.motor_asyncio import AsyncIOMotorDatabase


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


def mongo_user_serializer(user: User) -> dict:
    user_dict = asdict(user)
    user_dict["_id"] = user_dict.pop("id")
    return user_dict


def mongo_user_deserializer(user: dict) -> User:
    user_dict = user.copy()
    user_dict["id"] = user_dict.pop("_id")
    return from_dict(
        data_class=User,
        data=user_dict,
    )


class MongoUsersStorage(UsersStorageABC):
    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        serializer: Callable[[User], dict[str, Any]] = mongo_user_serializer,
        deserializer: Callable[[dict], User] = mongo_user_deserializer,
    ) -> None:
        self._collection = db["users"]
        self._serializer = serializer
        self._deserializer = deserializer

    async def get(self, id: str) -> User | None:
        user = await self._collection.find_one({"_id": id})
        return self._deserializer(dict(user)) if user else None

    async def get_by_nickname(self, nickname: str) -> User | None:
        user = await self._collection.find_one({"nickname": nickname})
        return self._deserializer(dict(user)) if user else None

    async def add(self, user: User) -> None:
        await self._collection.replace_one(
            {"_id": user.id},
            self._serializer(user),
            upsert=True,
        )
