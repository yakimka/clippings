import uuid

from clippings.books.ports import BookForGenerateId, ClippingForGenerateId
from clippings.utils.hash import hasher


def book_id_generator(book: BookForGenerateId) -> str:
    return hasher(f"{book.title}_{book.author}")


def clipping_id_generator(clipping: ClippingForGenerateId) -> str:
    return hasher(
        f"{clipping.page}_{clipping.location}_{clipping.content}_{clipping.added_at}"
    )


def inline_note_id_generator() -> str:
    return uuid.uuid4().hex
