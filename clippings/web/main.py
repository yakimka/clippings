from collections.abc import AsyncGenerator
from pathlib import Path
from random import randint  # noqa: DUO102

from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse, Response

from clippings.books.adapters.finders import MockBooksFinder
from clippings.books.adapters.id_generators import (
    book_id_generator,
    clipping_id_generator,
)
from clippings.books.adapters.readers import KindleClippingsReader
from clippings.books.adapters.storages import MockBooksStorage
from clippings.books.ports import BooksFinderABC, BooksStorageABC, ClippingsReaderABC
from clippings.books.presenters.books_detail_presenter import (
    BooksDetailHtmlRendered,
    BooksDetailPresenter,
)
from clippings.books.presenters.books_page_presenter import (
    BooksPageHtmlRendered,
    BooksPagePresenter,
)
from clippings.books.presenters.pagination_presenter import classic_pagination_presenter
from clippings.books.use_cases.import_clippings import ImportClippingsUseCase
from clippings.test.object_mother import ObjectMother

app = FastAPI()

mother = ObjectMother()
all_books = [
    mother.book(
        id=f"book:{i}",
        title=f"The Book {i}",
        clippings=[mother.clipping() for _ in range(randint(0, 10))],  # noqa: S311
    )
    for i in range(100)
]
books_map = {book.id: book for book in all_books}
books_map = {}


async def get_books_finder() -> BooksFinderABC:
    return MockBooksFinder(books_map)


async def get_books_storage() -> BooksStorageABC:
    return MockBooksStorage(books_map)


async def get_clippings_reader() -> AsyncGenerator[ClippingsReaderABC, None]:
    this_dir = Path(__file__).parent
    with open(this_dir / "My Clippings.txt", encoding="utf-8-sig") as file:
        yield KindleClippingsReader(file)


@app.get("/books/", response_class=HTMLResponse)
async def books(
    page: int = 1,
    on_page: int = 10,
    books_finder: BooksFinderABC = Depends(get_books_finder),
) -> str:
    books_presenter = BooksPagePresenter(
        finder=books_finder, pagination_presenter=classic_pagination_presenter
    )
    books_page_rendered = BooksPageHtmlRendered()
    books_dto = await books_presenter.present(page=page, on_page=on_page)
    return await books_page_rendered.render(books_dto)


@app.get("/books/import", response_class=HTMLResponse)
async def import_books(
    books_storage: BooksStorageABC = Depends(get_books_storage),
    clippings_reader: ClippingsReaderABC = Depends(get_clippings_reader),
) -> str:
    import_use_case = ImportClippingsUseCase(
        storage=books_storage,
        reader=clippings_reader,
        book_id_generator=book_id_generator,
        clipping_id_generator=clipping_id_generator,
    )
    await import_use_case.execute()
    return "Books imported"


@app.delete("/books/{book_id}", response_class=Response)
async def delete_book(book_id: str) -> Response:  # noqa: U100
    return Response(status_code=200)


@app.get("/books/{book_id}", response_class=HTMLResponse)
async def book_detail(
    book_id: str, books_storage: BooksStorageABC = Depends(get_books_storage)
) -> str:
    book_presenter = BooksDetailPresenter(storage=books_storage)
    book_page_rendered = BooksDetailHtmlRendered()
    book_dto = await book_presenter.present(book_id=book_id)
    return await book_page_rendered.render(book_dto)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "clippings.web.main:app",
        host="0.0.0.0",  # noqa: S104
        port=8000,
        reload=True,
        reload_dirs=["/opt/project/clippings/"],
    )
