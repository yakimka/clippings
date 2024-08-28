from dataclasses import dataclass

from clippings.books.ports import BooksStorageABC


@dataclass
class BookFieldsDTO:
    id: str
    title: str | None = None
    author: str | None = None
    cover_url: str | None = None
    rating: int | None = None
    review: str | None = None


class EditBookUseCase:
    def __init__(self, book_storage: BooksStorageABC):
        self._book_storage = book_storage

    async def execute(self, data: BookFieldsDTO) -> None:
        book = await self._book_storage.get(data.id)
        to_patch = {}
        if data.title is not None:
            to_patch["title"] = data.title
        if data.author is not None:
            to_patch["author"] = data.author
        if data.cover_url is not None:
            to_patch["cover_url"] = data.cover_url
        if data.rating is not None:
            to_patch["rating"] = data.rating
        if data.review is not None:
            to_patch["review"] = data.review

        if not to_patch:
            return

        for field, value in to_patch.items():
            setattr(book, field, value)

        await self._book_storage.add(book)
