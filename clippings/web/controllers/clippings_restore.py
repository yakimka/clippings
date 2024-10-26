from __future__ import annotations

from typing import TYPE_CHECKING, BinaryIO

from picodi import Provide, inject

from clippings.books.services import EnrichBooksMetaService
from clippings.books.use_cases.restore_data import RestoreDataUseCase
from clippings.deps import (
    get_book_info_client,
    get_books_storage,
    get_deleted_hash_storage,
)
from clippings.seedwork.exceptions import DomainError
from clippings.web.controllers.responses import HTMLResponse, Response

if TYPE_CHECKING:
    from clippings.books.ports import (
        BookInfoClientABC,
        BooksStorageABC,
        DeletedHashStorageABC,
    )


class ClippingsRestoreController:
    @inject
    def __init__(
        self,
        books_storage: BooksStorageABC = Provide(get_books_storage),
        deleted_hash_storage: DeletedHashStorageABC = Provide(get_deleted_hash_storage),
        book_info_client: BookInfoClientABC = Provide(get_book_info_client),
    ) -> None:
        self._books_storage = books_storage
        self._deleted_hash_storage = deleted_hash_storage
        self._book_info_client = book_info_client

    async def fire(self, backup: BinaryIO) -> Response:
        enrich_books_meta_service = EnrichBooksMetaService(self._book_info_client)
        use_case = RestoreDataUseCase(
            book_storage=self._books_storage,
            deleted_hash_storage=self._deleted_hash_storage,
            enrich_books_meta_service=enrich_books_meta_service,
        )
        result = await use_case.execute(backup)
        if isinstance(result, DomainError):
            return HTMLResponse(payload=str(result))
        return HTMLResponse(payload="Data restored")
