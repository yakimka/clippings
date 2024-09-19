from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clippings.users.exceptions import AuthError

if TYPE_CHECKING:
    from clippings.seedwork.exceptions import DomainError
    from clippings.users.ports import PasswordHasherABC, UsersStorageABC


@dataclass
class AuthUserDTO:
    id: str
    nickname: str


class AuthenticateUserUseCase:
    def __init__(
        self, users_storage: UsersStorageABC, password_hasher: PasswordHasherABC
    ) -> None:
        self._users_storage = users_storage
        self._password_hasher = password_hasher

    async def execute(self, nickname: str, password: str) -> AuthUserDTO | DomainError:
        user = await self._users_storage.get_by_nickname(nickname)
        if not user:
            return AuthError("User not found")
        if not user.check_password(password, self._password_hasher):
            return AuthError("Invalid password")

        return AuthUserDTO(id=user.id, nickname=user.nickname)
