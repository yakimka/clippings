from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response

from clippings.books.adapters.finders import MockBooksFinder
from clippings.books.adapters.storages import MockBooksStorage
from clippings.books.presenters.books_detail_presenter import (
    BooksDetailHtmlRendered,
    BooksDetailPresenter,
)
from clippings.books.presenters.books_page_presenter import (
    BooksPageHtmlRendered,
    BooksPagePresenter,
)
from clippings.books.presenters.pagination_presenter import classic_pagination_presenter
from clippings.test.object_mother import ObjectMother

app = FastAPI()

mother = ObjectMother()
all_books = [mother.book(id=f"book:{i}", title=f"The Book {i}") for i in range(100)]
books_map = {book.id: book for book in all_books}


@app.get("/books/", response_class=HTMLResponse)
async def books(
    page: int = 1,
    on_page: int = 10,
) -> str:
    books_finder = MockBooksFinder(books_map)
    books_presenter = BooksPagePresenter(
        finder=books_finder, pagination_presenter=classic_pagination_presenter
    )
    books_page_rendered = BooksPageHtmlRendered()
    books_dto = await books_presenter.present(page=page, on_page=on_page)
    return await books_page_rendered.render(books_dto)


@app.delete("/books/{book_id}", response_class=Response)
async def delete_book(book_id: str) -> Response:  # noqa: U100
    return Response(status_code=200)


@app.get("/books/{book_id}", response_class=HTMLResponse)
async def book_detail(book_id: str) -> str:
    books_storage = MockBooksStorage(books_map)
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
    )
