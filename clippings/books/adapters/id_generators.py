from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from clippings.utils.hash import hasher

if TYPE_CHECKING:
    from clippings.books.ports import BookForGenerateId, ClippingForGenerateId


def book_id_generator(book: BookForGenerateId) -> str:
    return hasher(f"{book.title}_{book.authors}")


def clipping_id_generator(clipping: ClippingForGenerateId) -> str:
    return hasher(f"{clipping.page}_{clipping.location}_{clipping.content}")


def inline_note_id_generator() -> str:
    return uuid.uuid4().hex
