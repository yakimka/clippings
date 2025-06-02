from __future__ import annotations

from typing import TYPE_CHECKING, BinaryIO

from picodi import Provide, inject

from clippings.books.services import EnrichBooksMetaService
from clippings.books.use_cases.restore_data import RestoreDataUseCase
from clippings.deps import (
    get_book_info_client,
    get_books_storage,
    get_deleted_hash_storage,
    get_users_storage,
)
from clippings.seedwork.exceptions import DomainError
from clippings.web.controllers.responses import HTMLResponse, Response

if TYPE_CHECKING:
    from clippings.books.ports import (
        BookInfoClientABC,
        BooksStorageABC,
        DeletedHashStorageABC,
    )
    from clippings.users.ports import UsersStorageABC


class ClippingsRestoreController:
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

    async def fire(self, backup: BinaryIO, user_id: str) -> Response:
        enrich_books_meta_service = EnrichBooksMetaService(self._book_info_client)
        use_case = RestoreDataUseCase(
            book_storage=self._books_storage,
            deleted_hash_storage=self._deleted_hash_storage,
            enrich_books_meta_service=enrich_books_meta_service,
            users_storage=self._users_storage,
        )
        try:
            result = await use_case.execute(backup, user_id=user_id)
        except Exception:  # noqa: PIE786
            return HTMLResponse(payload="Something went wrong while restoring data")
        if isinstance(result, DomainError):
            return HTMLResponse(payload=str(result))
        return HTMLResponse(payload="Data restored")
