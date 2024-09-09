from typing import BinaryIO

from picodi import Provide, inject

from clippings.books.adapters.id_generators import (
    book_id_generator,
    clipping_id_generator,
    inline_note_id_generator,
)
from clippings.books.adapters.readers import KindleClippingsReader
from clippings.books.ports import BooksStorageABC
from clippings.books.use_cases.import_clippings import ImportClippingsUseCase
from clippings.web.controllers.responses import HTMLResponse
from clippings.web.deps import get_books_storage
from clippings.web.presenters.book.clippings_import_page import (
    ClippingsImportPagePresenter,
)
from clippings.web.presenters.dtos import PresenterResult
from clippings.web.presenters.urls import urls_manager


class RenderClippingsImportPage:
    async def fire(self) -> HTMLResponse:
        presenter = ClippingsImportPagePresenter(urls_manager=urls_manager)
        result = await presenter.present()
        return HTMLResponse.from_presenter_result(result)


class ClippingsImportController:
    @inject
    def __init__(
        self, books_storage: BooksStorageABC = Provide(get_books_storage)
    ) -> None:
        self._books_storage = books_storage

    async def fire(self, file: BinaryIO) -> HTMLResponse:
        clippings_reader = KindleClippingsReader(file)
        import_use_case = ImportClippingsUseCase(
            storage=self._books_storage,
            reader=clippings_reader,
            book_id_generator=book_id_generator,
            clipping_id_generator=clipping_id_generator,
            inline_note_id_generator=inline_note_id_generator,
        )
        await import_use_case.execute()
        return HTMLResponse(payload="Books imported successfully")
