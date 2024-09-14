from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clippings.users.ports import PasswordHasherABC


@dataclass
class User:
    id: str
    nickname: str
    hashed_password: str

    def check_password(self, password: str, hasher: PasswordHasherABC) -> bool:
        return hasher.verify(password, self.hashed_password)
