from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clippings.seedwork.exceptions import DomainError
from clippings.users.entities import User

if TYPE_CHECKING:
    from clippings.users.ports import (
        PasswordHasherABC,
        UserIdGenerator,
        UsersStorageABC,
    )


@dataclass
class UserToCreateDTO:
    nickname: str
    password: str


class CreateUserUseCase:
    def __init__(
        self,
        users_storage: UsersStorageABC,
        user_id_generator: UserIdGenerator,
        password_hasher: PasswordHasherABC,
    ) -> None:
        self._users_storage = users_storage
        self._user_id_generator = user_id_generator
        self._password_hasher = password_hasher

    async def execute(self, user: UserToCreateDTO) -> str | DomainError:
        if len(user.password) < 8:
            return DomainError("Password must be at least 8 characters long")

        user_id = self._user_id_generator(user)
        if await self._users_storage.get_by_nickname(user.nickname):
            return DomainError(f"User with nickname '{user.nickname}' already exists")

        await self._users_storage.add(
            User(
                id=user_id,
                nickname=user.nickname,
                hashed_password=self._password_hasher.hash(user.password),
            )
        )
        return user_id
