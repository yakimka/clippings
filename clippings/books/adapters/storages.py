from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from dacite import Config, from_dict
from pymongo import ReplaceOne

from clippings.books.entities import Book, DeletedHash
from clippings.books.ports import BooksStorageABC, DeletedHashStorageABC

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Mapping

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

    async def find(
        self, query: BooksStorageABC.FindQuery = BooksStorageABC.DEFAULT_FIND_QUERY
    ) -> list[Book]:
        return [book async for book in self.find_iter(query)]

    async def find_iter(
        self, query: BooksStorageABC.FindQuery = BooksStorageABC.DEFAULT_FIND_QUERY
    ) -> AsyncGenerator[Book, None]:
        books = sorted(self.books.values(), key=lambda b: (b.title, b.id))
        start = query.start
        if query.limit is None:
            for book in books[start:]:
                yield book
            return
        end = start + query.limit
        for book in books[start:end]:
            yield book

    async def count(self, query: BooksStorageABC.FindQuery) -> int:
        return len(await self.find(query))

    async def distinct_authors(self) -> list[str]:
        return list({author for book in self.books.values() for author in book.authors})


def mongo_book_serializer(book: Book, user_id: str) -> dict:
    book_dict = asdict(book)
    book_dict["_id"] = f"{user_id}|{book_dict['id']}"
    book_dict["user_id"] = user_id
    for clipping in book_dict["clippings"]:
        clipping["type"] = clipping["type"].value
    return book_dict


def mongo_book_deserializer(book: dict) -> Book:
    book_dict = book.copy()
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
        book = await self._collection.find_one({"id": id, "user_id": self._user_id})
        return self._deserializer(dict(book)) if book else None

    async def get_many(self, ids: list[str]) -> list[Book]:
        books = await self._collection.find(
            {"id": {"$in": ids}, "user_id": self._user_id}
        ).to_list(None)
        return [self._deserializer(dict(book)) for book in books]

    async def add(self, book: Book) -> None:
        await self._collection.replace_one(
            {"id": book.id, "user_id": self._user_id},
            self._serializer(book, self._user_id),
            upsert=True,
        )

    async def extend(self, books: list[Book]) -> None:
        operations: list[ReplaceOne[Mapping[str, Any]]] = [
            ReplaceOne(
                {"id": book.id, "user_id": self._user_id},
                self._serializer(book, self._user_id),
                upsert=True,
            )
            for book in books
        ]
        await self._collection.bulk_write(operations)

    async def remove(self, book: Book) -> None:
        await self._collection.delete_one({"id": book.id, "user_id": self._user_id})

    async def find(
        self, query: BooksStorageABC.FindQuery = BooksStorageABC.DEFAULT_FIND_QUERY
    ) -> list[Book]:
        return [book async for book in self.find_iter(query)]

    async def find_iter(
        self, query: BooksStorageABC.FindQuery = BooksStorageABC.DEFAULT_FIND_QUERY
    ) -> AsyncGenerator[Book, None]:
        if query.limit == 0:
            return

        cursor = (
            self._collection.find({"user_id": self._user_id})
            .sort([("title", 1), ("id", 1)])
            .skip(query.start)
        )
        if query.limit is not None:
            cursor = cursor.limit(query.limit)

        async for book in cursor:
            yield self._deserializer(dict(book))

    async def count(self, query: BooksStorageABC.FindQuery) -> int:
        if query.limit == 0:
            return 0

        pipeline: list[dict[str, Any]] = [
            {"$match": {"user_id": self._user_id}},
            {"$skip": query.start},
        ]

        if query.limit is not None:
            pipeline.append({"$limit": query.limit})

        pipeline.append({"$count": "total"})

        result = await self._collection.aggregate(pipeline).to_list(None)

        return result[0]["total"] if result else 0

    async def distinct_authors(self) -> list[str]:
        pipeline: list[dict[str, Any]] = [
            {"$match": {"user_id": self._user_id}},
            {"$unwind": "$authors"},
            {"$group": {"_id": "$authors"}},
        ]
        result = await self._collection.aggregate(pipeline).to_list(None)
        return [doc["_id"] for doc in result]


class MockDeletedHashStorage(DeletedHashStorageABC):
    def __init__(self, hashes_map: dict[str, DeletedHash] | None = None) -> None:
        self.hashes: dict[str, DeletedHash] = {} if hashes_map is None else hashes_map

    async def get_all(self) -> list[DeletedHash]:
        return list(self.hashes.values())

    async def add(self, deleted_hash: DeletedHash) -> None:
        self.hashes[deleted_hash.id] = deleted_hash

    async def extend(self, deleted_hashes: list[DeletedHash]) -> None:
        self.hashes.update({hash.id: hash for hash in deleted_hashes})

    async def clear(self) -> None:
        self.hashes.clear()


class MongoDeletedHashStorage(DeletedHashStorageABC):
    def __init__(self, db: AsyncIOMotorDatabase, user_id: str) -> None:
        self._collection = db["deleted_hashes"]
        self._user_id = user_id

    async def get_all(self) -> list[DeletedHash]:
        docs = await self._collection.find({"user_id": self._user_id}).to_list(None)
        return [DeletedHash(doc["_id"]) for doc in docs]

    async def add(self, hash: DeletedHash) -> None:
        doc = {"_id": hash.id, "user_id": self._user_id}
        await self._collection.replace_one({"_id": hash.id}, doc, upsert=True)

    async def extend(self, hashes: list[DeletedHash]) -> None:
        operations: list[ReplaceOne[Mapping[str, Any]]] = [
            ReplaceOne(
                {"_id": hash.id, "user_id": self._user_id},
                {"_id": hash.id, "user_id": self._user_id},
                upsert=True,
            )
            for hash in hashes
        ]
        await self._collection.bulk_write(operations)

    async def clear(self) -> None:
        await self._collection.delete_many({"user_id": self._user_id})
