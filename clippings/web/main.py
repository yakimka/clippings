from fastapi import Depends, FastAPI, Form, UploadFile
from fastapi.responses import HTMLResponse, Response
from starlette.responses import RedirectResponse

from clippings.books.adapters.finders import MockBooksFinder
from clippings.books.adapters.id_generators import (
    book_id_generator,
    clipping_id_generator,
    inline_note_id_generator,
)
from clippings.books.adapters.readers import KindleClippingsReader
from clippings.books.adapters.storages import MockBooksStorage
from clippings.books.entities import Book
from clippings.books.ports import BooksFinderABC, BooksStorageABC
from clippings.books.use_cases.edit_book import (
    AddInlineNoteUseCase,
    ClippingFieldsDTO,
    DeleteInlineNoteUseCase,
    EditBookUseCase,
    EditClippingUseCase,
    EditInlineNoteUseCase,
    RatingDTO,
    ReviewDTO,
    TitleDTO,
    UnlinkInlineNoteUseCase,
)
from clippings.books.use_cases.import_clippings import ImportClippingsUseCase
from clippings.web.presenters.book.clippings_import_page import (
    ClippingsImportPagePresenter,
)
from clippings.web.presenters.book.detail.forms import (
    AddInlineNoteFormPresenter,
    EditBookInfoFormPresenter,
    EditBookReviewFormPresenter,
    EditClippingFormPresenter,
    EditInlineNoteFormPresenter,
)
from clippings.web.presenters.book.detail.page import (
    BookDetailPagePart,
    BookDetailPagePresenter,
    ClippingPart,
    ClippingPresenter,
)
from clippings.web.presenters.book.list_page import BooksListPagePresenter
from clippings.web.presenters.book.urls import make_book_urls
from clippings.web.presenters.pagination import classic_pagination_calculator
from clippings.web.presenters.urls import UrlsManager


@app.get("/books/", response_class=HTMLResponse)
async def book_list(
    page: int = 1,
    on_page: int = 10,
    books_finder: BooksFinderABC = Depends(get_books_finder),
) -> str:
    presenter = BooksListPagePresenter(
        finder=books_finder,
        pagination_calculator=classic_pagination_calculator,
        urls_manager=urls_manager,
    )
    result = await presenter.present(page=page, on_page=on_page)
    return result.render()


@app.get("/", response_class=RedirectResponse, status_code=302)
async def redirect_to_books() -> str:
    return "/books/"


@app.delete("/books/{book_id}", response_class=Response)
async def delete_book(book_id: str) -> Response:  # noqa: U100
    return Response(status_code=200)


@app.put("/books/{book_id}/review", response_class=RedirectResponse, status_code=303)
async def save_book_review(
    book_id: str,
    review: str = Form(""),
    books_storage: BooksStorageABC = Depends(get_books_storage),
) -> str:
    use_case = EditBookUseCase(book_storage=books_storage)
    await use_case.execute(
        book_id,
        fields=[ReviewDTO(review=review)],
    )
    return f"/books/{book_id}/review"


@app.put("/books/{book_id}/info", response_class=RedirectResponse, status_code=303)
async def book_info_save(
    book_id: str,
    title: str = Form(),
    authors: str = Form(),
    rating: int = Form(),
    books_storage: BooksStorageABC = Depends(get_books_storage),
) -> str:
    use_case = EditBookUseCase(book_storage=books_storage)
    await use_case.execute(
        book_id,
        fields=[
            TitleDTO(title=title, authors=authors.split(" & ")),
            RatingDTO(rating=rating),
        ],
    )
    return f"/books/{book_id}/info"


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
def delete_clipping(book_id: str, clipping_id: str) -> Response:  # noqa: U100
    return Response(status_code=200)


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
    use_case = AddInlineNoteUseCase(
        book_storage=books_storage, inline_note_id_generator=inline_note_id_generator
    )
    await use_case.execute(book_id=book_id, clipping_id=clipping_id, content=content)
    return f"/books/{book_id}/clippings/{clipping_id}"


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
