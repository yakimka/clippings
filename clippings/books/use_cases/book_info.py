from clippings.books.dtos import BookInfoSearchResultDTO
from clippings.books.ports import BookInfoClientABC


class MockBookInfoClient(BookInfoClientABC):
    def __init__(self) -> None:
        image_ids = [
            "N6EGEAAAQBAJ",
            "MoEO9onVftUC",
            "zFheDgAAQBAJ",
        ]

        def make_google_books_img_urls(id: str, zoom: int) -> str:
            return (
                f"https://books.google.com/books/content?id={id}"
                f"&printsec=frontcover&img=1&zoom={zoom}"
            )

        self._images = [
            (None, None),
            *[
                (make_google_books_img_urls(id, 1), make_google_books_img_urls(id, 3))
                for id in image_ids
            ],
        ]

    async def get(
        self, title: str, author: str | None = None
    ) -> BookInfoSearchResultDTO | None:
        title_len = len(title)
        if title_len % 2 == 0:
            return None

        small_img, large_img = self._images[title_len % len(self._images)]
        return BookInfoSearchResultDTO(
            isbns=[],
            title=title,
            authors=[author] if author else [],
            description="Nice book",
            cover_image_small=small_img,
            cover_image_big=large_img,
        )
