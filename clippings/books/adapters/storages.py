from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from dacite import Config, from_dict
from pymongo import ReplaceOne

from clippings.books.entities import Book
from clippings.books.ports import BooksStorageABC

if TYPE_CHECKING:
    from collections.abc import Callable

    from motor.motor_asyncio import AsyncIOMotorDatabase


class MockBooksStorage(BooksStorageABC):
    def __init__(self, books_map: dict[str, Book] | None = None) -> None:
        self.books: dict[str, Book] = {} if books_map is None else books_map

    async def get(self, id: str) -> Book | None:
        return self.books.get(id)

    async def get_many(self, ids: list[str]) -> list[Book]:
        books = []
        for id in ids:
            if book := self.books.get(id):
                books.append(book)
        return books

    async def add(self, book: Book) -> None:
        self.books[book.id] = book

    async def extend(self, books: list[Book]) -> None:
        for book in books:
            await self.add(book)

    async def remove(self, book: Book) -> None:
        self.books.pop(book.id, None)


def mongo_book_serializer(book: Book, user_id: str) -> dict:
    book_dict = asdict(book)
    book_dict["_id"] = book_dict.pop("id")
    book_dict["user_id"] = user_id
    for clipping in book_dict["clippings"]:
        clipping["type"] = clipping["type"].value
    return book_dict


def mongo_book_deserializer(book: dict) -> Book:
    book_dict = book.copy()
    book_dict["id"] = book_dict.pop("_id")
    return from_dict(
        data_class=Book,
        data=book_dict,
        config=Config(forward_references={"datetime": datetime}, cast=[tuple, Enum]),
    )


class MongoBooksStorage(BooksStorageABC):
    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        user_id: str,
        serializer: Callable[[Book, str], dict[str, Any]] = mongo_book_serializer,
        deserializer: Callable[[dict], Book] = mongo_book_deserializer,
    ) -> None:
        self._collection = db["books"]
        self._user_id = user_id
        self._serializer = serializer
        self._deserializer = deserializer

    async def get(self, id: str) -> Book | None:
        book = await self._collection.find_one({"_id": id, "user_id": self._user_id})
        return self._deserializer(dict(book)) if book else None

    async def get_many(self, ids: list[str]) -> list[Book]:
        books = await self._collection.find(
            {"_id": {"$in": ids}, "user_id": self._user_id}
        ).to_list(None)
        return [self._deserializer(dict(book)) for book in books]

    async def add(self, book: Book) -> None:
        await self._collection.replace_one(
            {"_id": book.id},
            self._serializer(book, self._user_id),
            upsert=True,
        )

    async def extend(self, books: list[Book]) -> None:
        operations: list[ReplaceOne[Mapping[str, Any]]] = [
            ReplaceOne(
                {"_id": book.id}, self._serializer(book, self._user_id), upsert=True
            )
            for book in books
        ]
        await self._collection.bulk_write(operations)

    async def remove(self, book: Book) -> None:
        await self._collection.delete_one({"_id": book.id})
