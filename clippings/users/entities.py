from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clippings.users.ports import PasswordHasherABC


@dataclass
class User:
    id: str
    nickname: str
    hashed_password: str | None
    max_books: int = field(default=100)
    max_clippings_per_book: int = field(default=500)

    def set_password(self, password: str, hasher: PasswordHasherABC) -> None:
        self.hashed_password = hasher.hash(password)

    def check_password(self, password: str, hasher: PasswordHasherABC) -> bool:
        if self.hashed_password is None:
            return False
        return hasher.verify(password, self.hashed_password)
