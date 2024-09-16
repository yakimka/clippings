from __future__ import annotations

from typing import TYPE_CHECKING, Any

from clippings.books.adapters.storages import mongo_book_deserializer
from clippings.books.ports import BooksFinderABC, FinderQuery

if TYPE_CHECKING:
    from collections.abc import Callable

    from motor.motor_asyncio import AsyncIOMotorDatabase

    from clippings.books.entities import Book


_default_query = FinderQuery()


class MockBooksFinder(BooksFinderABC):
    def __init__(self, books_map: dict[str, Book] | None = None) -> None:
        self.books: dict[str, Book] = {} if books_map is None else books_map

    async def find(self, query: FinderQuery = _default_query) -> list[Book]:
        books = sorted(self.books.values(), key=lambda b: (b.title, b.id))
        start = query.start
        if query.limit is None:
            return books[start:]
        end = start + query.limit
        return books[start:end]

    async def count(self, query: FinderQuery) -> int:
        return len(await self.find(query))


class MongoBooksFinder(BooksFinderABC):
    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        user_id: str,
        deserializer: Callable[[dict], Book] = mongo_book_deserializer,
    ) -> None:
        self._collection = db["books"]
        self._user_id = user_id
        self._deserializer = deserializer

    async def find(self, query: FinderQuery = _default_query) -> list[Book]:
        cursor = (
            self._collection.find({"user_id": self._user_id})
            .sort("title", 1)
            .skip(query.start)
        )
        if query.limit is not None:
            cursor = cursor.limit(query.limit)
        books = await cursor.to_list(None)
        return [self._deserializer(dict(book)) for book in books]

    async def count(self, query: FinderQuery) -> int:
        pipeline: list[dict[str, Any]] = [
            {"$match": {"user_id": self._user_id}},
            {"$skip": query.start},
        ]

        if query.limit is not None:
            pipeline.append({"$limit": query.limit})

        pipeline.append({"$count": "total"})

        result = await self._collection.aggregate(pipeline).to_list(None)

        if result:
            return result[0]["total"]
        return 0
