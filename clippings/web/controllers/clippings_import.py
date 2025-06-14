from __future__ import annotations

from typing import TYPE_CHECKING, BinaryIO

from picodi import Provide, inject

from clippings.books.adapters.id_generators import (
    book_id_generator,
    clipping_id_generator,
    inline_note_id_generator,
)
from clippings.books.adapters.readers import KindleClippingsReader
from clippings.books.services import EnrichBooksMetaService
from clippings.books.use_cases.import_clippings import ImportClippingsUseCase
from clippings.deps import (
    get_book_info_client,
    get_books_storage,
    get_deleted_hash_storage,
    get_users_storage,
)
from clippings.web.controllers.responses import HTMLResponse
from clippings.web.presenters.book.clippings_import_page import (
    ClippingsImportPagePresenter,
    ImportClippingsResultPresenter,
)
from clippings.web.presenters.urls import urls_manager

if TYPE_CHECKING:
    from clippings.books.ports import (
        BookInfoClientABC,
        BooksStorageABC,
        DeletedHashStorageABC,
    )
    from clippings.users.ports import UsersStorageABC


class RenderClippingsImportPageController:
    async def fire(self) -> HTMLResponse:
        presenter = ClippingsImportPagePresenter(urls_manager=urls_manager)
        result = await presenter.present()
        return HTMLResponse.from_presenter_result(result)


class ClippingsImportController:
    @inject
    def __init__(
        self,
        books_storage: BooksStorageABC = Provide(get_books_storage),
        deleted_hash_storage: DeletedHashStorageABC = Provide(get_deleted_hash_storage),
        book_info_client: BookInfoClientABC = Provide(get_book_info_client),
        users_storage: UsersStorageABC = Provide(get_users_storage),
    ) -> None:
        self._books_storage = books_storage
        self._deleted_hash_storage = deleted_hash_storage
        self._book_info_client = book_info_client
        self._users_storage = users_storage

    async def fire(self, file: BinaryIO, user_id: str) -> HTMLResponse:
        clippings_reader = KindleClippingsReader(file)
        enrich_books_meta_service = EnrichBooksMetaService(self._book_info_client)
        import_use_case = ImportClippingsUseCase(
            storage=self._books_storage,
            reader=clippings_reader,
            deleted_hash_storage=self._deleted_hash_storage,
            enrich_books_meta_service=enrich_books_meta_service,
            book_id_generator=book_id_generator,
            clipping_id_generator=clipping_id_generator,
            inline_note_id_generator=inline_note_id_generator,
            users_storage=self._users_storage,
        )
        statistics = await import_use_case.execute(user_id)

        presenter = ImportClippingsResultPresenter()
        result = await presenter.present(statistics)
        return HTMLResponse.from_presenter_result(result)
