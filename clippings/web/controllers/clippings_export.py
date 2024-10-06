from __future__ import annotations

from typing import TYPE_CHECKING

from picodi import Provide, inject

from clippings.books.use_cases.export_data import ExportDataUseCase
from clippings.deps import get_books_storage, get_deleted_hash_storage
from clippings.web.controllers.responses import Response, StreamingResponse

if TYPE_CHECKING:
    from clippings.books.ports import BooksStorageABC, DeletedHashStorageABC


class ClippingsExportController:
    @inject
    def __init__(
        self,
        books_storage: BooksStorageABC = Provide(get_books_storage),
        deleted_hash_storage: DeletedHashStorageABC = Provide(get_deleted_hash_storage),
    ) -> None:
        self._books_storage = books_storage
        self._deleted_hash_storage = deleted_hash_storage

    async def fire(self) -> Response:
        use_case = ExportDataUseCase(
            book_storage=self._books_storage,
            deleted_hash_storage=self._deleted_hash_storage,
        )
        result = await use_case.execute()
        return StreamingResponse(
            payload=result.iterator,
            media_type="application/x-json-stream",
            headers={
                "Content-Disposition": f"attachment; filename={result.filename}",
            },
        )
