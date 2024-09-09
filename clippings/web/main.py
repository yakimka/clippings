from fastapi import Depends, Form
from fastapi.responses import Response
from starlette.responses import RedirectResponse

from clippings.books.adapters.id_generators import inline_note_id_generator
from clippings.books.ports import BooksStorageABC
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


@app.delete("/books/{book_id}", response_class=Response)
async def delete_book(book_id: str) -> Response:  # noqa: U100
    return Response(status_code=200)


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
