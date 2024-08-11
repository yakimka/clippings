from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clippings.books.ports import BooksStorageABC, ClippingsReaderABC


class ImportClippingsUseCase:
    def __init__(self, storage: BooksStorageABC, reader: ClippingsReaderABC):
        self._storage = storage
        self._reader = reader

    async def execute(self) -> None:
        pass
