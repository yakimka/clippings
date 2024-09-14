from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clippings.users.ports import UserForGenerateId


def user_id_generator(user: UserForGenerateId) -> str:  # noqa: U100
    return uuid.uuid4().hex
