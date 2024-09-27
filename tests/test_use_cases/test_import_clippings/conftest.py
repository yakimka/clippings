from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from clippings.books.ports import BookIdGenerator


@pytest.fixture()
def autoincrement_id_generator() -> BookIdGenerator:
    ids = (str(i) for i in range(1, 1000))
    return lambda _: str(next(ids))
