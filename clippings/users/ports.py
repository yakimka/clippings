from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from clippings.users.entities import User


class UsersStorageABC(abc.ABC):
    @abc.abstractmethod
    async def get(self, id: str) -> User | None:
        pass

    @abc.abstractmethod
    async def get_by_nickname(self, nickname: str) -> User | None:
        pass

    @abc.abstractmethod
    async def add(self, user: User) -> None:
        pass


class UserForGenerateId(Protocol):
    nickname: str


class UserIdGenerator(Protocol):
    def __call__(self, user: UserForGenerateId) -> str:
        pass


class PasswordHasherABC(abc.ABC):
    @abc.abstractmethod
    def hash(self, password: str) -> str:
        pass

    @abc.abstractmethod
    def verify(self, password: str, hashed_password: str) -> bool:
        pass
