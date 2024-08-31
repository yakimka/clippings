from collections.abc import AsyncGenerator
from pathlib import Path

from fastapi import Depends, FastAPI, Form
from fastapi.responses import HTMLResponse, Response
from starlette.responses import RedirectResponse

from clippings.books.adapters.finders import MockBooksFinder
from clippings.books.adapters.id_generators import (
    book_id_generator,
    clipping_id_generator,
)
from clippings.books.adapters.readers import KindleClippingsReader
from clippings.books.adapters.storages import MockBooksStorage
from clippings.books.ports import BooksFinderABC, BooksStorageABC, ClippingsReaderABC
from clippings.books.presenters import html_renderers
from clippings.books.presenters.book_detail.presenters import BookDetailPresenter
from clippings.books.presenters.book_list import BooksPagePresenter
from clippings.books.presenters.pagination import classic_pagination_presenter
from clippings.books.presenters.urls import UrlsManager, make_books_urls_builder
from clippings.books.use_cases.edit_book import (
    AddInlineNoteUseCase,
    BookFieldsDTO,
    ClippingFieldsDTO,
    DeleteInlineNoteUseCase,
    EditBookUseCase,
    EditClippingUseCase,
    EditInlineNoteUseCase,
    UnlinkInlineNoteUseCase,
)
from clippings.books.use_cases.import_clippings import ImportClippingsUseCase

app = FastAPI()
books_map = {}
book_urls_builder = make_books_urls_builder()
urls_manager = UrlsManager(book_urls_builder())


async def get_books_finder() -> BooksFinderABC:
    return MockBooksFinder(books_map)


async def get_books_storage() -> BooksStorageABC:
    return MockBooksStorage(books_map)


async def get_clippings_reader() -> AsyncGenerator[ClippingsReaderABC, None]:
    this_dir = Path(__file__).parent
    with open(this_dir / "My Clippings.txt", encoding="utf-8-sig") as file:
        yield KindleClippingsReader(file)


async def get_book_detail_presenter(
    books_storage: BooksStorageABC = Depends(get_books_storage),
) -> BookDetailPresenter:
    return BookDetailPresenter(storage=books_storage, urls_manager=urls_manager)


@app.get("/books/", response_class=HTMLResponse)
async def book_list(
    page: int = 1,
    on_page: int = 10,
    books_finder: BooksFinderABC = Depends(get_books_finder),
) -> str:
    books_presenter = BooksPagePresenter(
        finder=books_finder,
        pagination_presenter=classic_pagination_presenter,
        urls_manager=urls_manager,
    )
    books_dto = await books_presenter.present(page=page, on_page=on_page)
    return html_renderers.book_list(books_dto)


@app.get("/books/import", response_class=HTMLResponse)
async def clippings_import(
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
    book_id: str,
    detail_presenter: BookDetailPresenter = Depends(get_book_detail_presenter),
) -> str:
    book_dto = await detail_presenter.page(book_id=book_id)
    return html_renderers.book_detail(book_dto)


@app.get("/books/{book_id}/review", response_class=HTMLResponse)
async def book_review(
    book_id: str,
    detail_presenter: BookDetailPresenter = Depends(get_book_detail_presenter),
) -> str:
    dto = await detail_presenter.review(book_id=book_id)
    return html_renderers.book_review(dto)


@app.get("/books/{book_id}/review/edit", response_class=HTMLResponse)
async def book_review_update_form(
    book_id: str,
    detail_presenter: BookDetailPresenter = Depends(get_book_detail_presenter),
) -> str:
    dto = await detail_presenter.edit_review(book_id=book_id)
    return html_renderers.book_review_update_form(dto)


@app.put("/books/{book_id}/review", response_class=RedirectResponse, status_code=303)
async def save_book_review(
    book_id: str,
    review: str = Form(""),
    books_storage: BooksStorageABC = Depends(get_books_storage),
) -> str:
    use_case = EditBookUseCase(book_storage=books_storage)
    await use_case.execute(
        BookFieldsDTO(
            id=book_id,
            review=review,
        )
    )
    return f"/books/{book_id}/review"


@app.get("/books/{book_id}/info", response_class=HTMLResponse)
async def book_info(
    book_id: str,
    detail_presenter: BookDetailPresenter = Depends(get_book_detail_presenter),
) -> str:
    dto = await detail_presenter.book_info(book_id=book_id)
    return html_renderers.book_info(dto)


@app.get("/books/{book_id}/info/edit", response_class=HTMLResponse)
async def book_info_update_form(
    book_id: str,
    detail_presenter: BookDetailPresenter = Depends(get_book_detail_presenter),
) -> str:
    dto = await detail_presenter.edit_book_info(book_id=book_id)
    return html_renderers.book_info_update_form(dto)


@app.put("/books/{book_id}/info", response_class=RedirectResponse, status_code=303)
async def book_info_save(
    book_id: str,
    title: str = Form(),
    author: str = Form(),
    rating: int = Form(),
    books_storage: BooksStorageABC = Depends(get_books_storage),
) -> str:
    use_case = EditBookUseCase(book_storage=books_storage)
    await use_case.execute(
        BookFieldsDTO(
            id=book_id,
            title=title,
            author=author,
            rating=rating,
        )
    )
    return f"/books/{book_id}/info"


@app.get("/books/{book_id}/clippings", response_class=HTMLResponse)
async def clipping_list(
    book_id: str,
    detail_presenter: BookDetailPresenter = Depends(get_book_detail_presenter),
) -> str:
    dto = await detail_presenter.clippings(book_id=book_id)
    return html_renderers.clipping_list(dto)


@app.get("/books/{book_id}/clippings/{clipping_id}", response_class=HTMLResponse)
async def clipping_detail(
    book_id: str,
    clipping_id: str,
    detail_presenter: BookDetailPresenter = Depends(get_book_detail_presenter),
) -> str:
    dto = await detail_presenter.clipping(book_id=book_id, clipping_id=clipping_id)
    return html_renderers.clipping_detail(dto)


@app.get("/books/{book_id}/clippings/{clipping_id}/edit", response_class=HTMLResponse)
async def edit_clipping_form(
    book_id: str,
    clipping_id: str,
    detail_presenter: BookDetailPresenter = Depends(get_book_detail_presenter),
) -> str:
    dto = await detail_presenter.edit_clipping(book_id=book_id, clipping_id=clipping_id)
    return html_renderers.clipping_update_form(dto)


@app.put(
    "/books/{book_id}/clippings/{clipping_id}",
    response_class=RedirectResponse,
    status_code=303,
)
async def save_clipping(
    book_id: str,
    clipping_id: str,
    content: str = Form(),
    books_storage: BooksStorageABC = Depends(get_books_storage),
) -> str:
    use_case = EditClippingUseCase(book_storage=books_storage)
    await use_case.execute(
        ClippingFieldsDTO(
            id=clipping_id,
            book_id=book_id,
            content=content,
        )
    )
    return f"/books/{book_id}/clippings/{clipping_id}"


@app.delete("/books/{book_id}/clippings/{clipping_id}", response_class=Response)
def delete_clipping(book_id: str, clipping_id: str) -> Response:
    return Response(status_code=200)


@app.get(
    "/books/{book_id}/clippings/{clipping_id}/inline_notes/add",
    response_class=HTMLResponse,
)
async def add_inline_note(
    book_id: str,
    clipping_id: str,
    detail_presenter: BookDetailPresenter = Depends(get_book_detail_presenter),
) -> str:
    dto = await detail_presenter.add_inline_note(
        book_id=book_id, clipping_id=clipping_id
    )
    return html_renderers.inline_note_add_form(dto)


@app.post(
    "/books/{book_id}/clippings/{clipping_id}/inline_notes",
    response_class=RedirectResponse,
    status_code=303,
)
async def add_inline_note(
    book_id: str,
    clipping_id: str,
    content: str = Form(),
    books_storage: BooksStorageABC = Depends(get_books_storage),
) -> str:
    use_case = AddInlineNoteUseCase(book_storage=books_storage)
    await use_case.execute(book_id=book_id, clipping_id=clipping_id, content=content)
    return f"/books/{book_id}/clippings/{clipping_id}"


@app.get(
    "/books/{book_id}/clippings/{clipping_id}/inline_notes/{inline_note_id}/edit",
    response_class=HTMLResponse,
)
async def edit_inline_note_form(
    book_id: str,
    clipping_id: str,
    inline_note_id: str,
    detail_presenter: BookDetailPresenter = Depends(get_book_detail_presenter),
) -> Response:
    dto = await detail_presenter.edit_inline_note(
        book_id=book_id, clipping_id=clipping_id, inline_note_id=inline_note_id
    )
    return html_renderers.inline_note_update_form(dto)


@app.put(
    "/books/{book_id}/clippings/{clipping_id}/inline_notes/{inline_note_id}",
    response_class=RedirectResponse,
    status_code=303,
)
async def save_inline_note(
    book_id: str,
    clipping_id: str,
    inline_note_id: str,
    content: str = Form(),
    books_storage: BooksStorageABC = Depends(get_books_storage),
) -> str:
    use_case = EditInlineNoteUseCase(book_storage=books_storage)
    await use_case.execute(
        book_id=book_id,
        clipping_id=clipping_id,
        inline_note_id=inline_note_id,
        content=content,
    )
    return f"/books/{book_id}/clippings/{clipping_id}"


@app.delete(
    "/books/{book_id}/clippings/{clipping_id}/inline_notes/{inline_note_id}",
    response_class=RedirectResponse,
    status_code=303,
)
async def delete_inline_note(
    book_id: str,
    clipping_id: str,
    inline_note_id: str,
    books_storage: BooksStorageABC = Depends(get_books_storage),
) -> str:
    use_case = DeleteInlineNoteUseCase(book_storage=books_storage)
    await use_case.execute(
        book_id=book_id,
        clipping_id=clipping_id,
        inline_note_id=inline_note_id,
    )
    return f"/books/{book_id}/clippings/{clipping_id}"


@app.post(
    "/books/{book_id}/clippings/{clipping_id}/inline_notes/{inline_note_id}/unlink",
    response_class=RedirectResponse,
    status_code=303,
)
async def unlink_inline_note(
    book_id: str,
    clipping_id: str,
    inline_note_id: str,
    books_storage: BooksStorageABC = Depends(get_books_storage),
) -> str:
    use_case = UnlinkInlineNoteUseCase(book_storage=books_storage)
    await use_case.execute(
        book_id=book_id,
        clipping_id=clipping_id,
        inline_note_id=inline_note_id,
    )
    return f"/books/{book_id}/clippings"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "clippings.web.main:app",
        host="0.0.0.0",  # noqa: S104
        port=8000,
        reload=True,
        reload_dirs=["/opt/project/clippings/"],
    )
