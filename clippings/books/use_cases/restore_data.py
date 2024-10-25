from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from dacite import Config, from_dict
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from clippings.books.constants import (
    BOOK_AUTHOR_MAX_LENGTH,
    BOOK_MAX_AUTHORS,
    BOOK_MAX_CLIPPINGS,
    BOOK_REVIEW_MAX_LENGTH,
    BOOK_TITLE_MAX_LENGTH,
    CLIPPING_CONTENT_MAX_LENGTH,
    CLIPPING_MAX_INLINE_NOTES,
)
from clippings.books.entities import Book, DeletedHash
from clippings.seedwork.exceptions import DomainError

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from clippings.books.ports import BooksStorageABC, DeletedHashStorageABC

DATA_SCHEMA = {
    "type": "object",
    "oneOf": [
        {
            "properties": {
                "type": {"type": "string", "enum": ["book"]},
                "id": {"type": "string", "pattern": "^[A-Z0-9]+$", "maxLength": 13},
                "title": {"type": "string", "maxLength": BOOK_TITLE_MAX_LENGTH},
                "authors": {
                    "type": "array",
                    "items": {"type": "string", "maxLength": BOOK_AUTHOR_MAX_LENGTH},
                    "maxItems": BOOK_MAX_AUTHORS,
                },
                "review": {"type": "string", "maxLength": BOOK_REVIEW_MAX_LENGTH},
                "rating": {"type": ["null", "number"]},
                "clippings": {
                    "type": "array",
                    "maxItems": BOOK_MAX_CLIPPINGS,
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "page": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "minItems": 2,
                                "maxItems": 2,
                            },
                            "location": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "minItems": 2,
                                "maxItems": 2,
                            },
                            "type": {"type": "string", "enum": ["highlight", "note"]},
                            "content": {
                                "type": "string",
                                "maxLength": CLIPPING_CONTENT_MAX_LENGTH,
                            },
                            "added_at": {"type": "string", "format": "date-time"},
                            "inline_notes": {
                                "type": "array",
                                "maxItems": CLIPPING_MAX_INLINE_NOTES,
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string", "maxLength": 32},
                                        "content": {
                                            "type": "string",
                                            "maxLength": CLIPPING_CONTENT_MAX_LENGTH,
                                        },
                                        "original_id": {
                                            "type": "string",
                                            "pattern": "^[A-Z0-9]+$",
                                            "maxLength": 13,
                                        },
                                        "automatically_linked": {"type": "boolean"},
                                    },
                                    "required": [
                                        "id",
                                        "content",
                                        "original_id",
                                        "automatically_linked",
                                    ],
                                },
                            },
                        },
                        "required": [
                            "id",
                            "page",
                            "location",
                            "type",
                            "content",
                            "added_at",
                            "inline_notes",
                        ],
                    },
                    "required": [
                        "type",
                        "id",
                        "title",
                        "authors",
                        "review",
                        "rating",
                        "clippings",
                    ],
                },
            },
        },
        {
            "properties": {
                "type": {"type": "string", "enum": ["deleted_hash"]},
                "id": {"type": "string"},
            },
            "required": ["type", "id"],
        },
    ],
}


class InvalidDataError(DomainError):
    pass


def validate_format(data: dict) -> None | InvalidDataError:
    try:
        validate(instance=data, schema=DATA_SCHEMA)
    except ValidationError as e:
        return InvalidDataError(e.message)
    return None


def book_json_deserializer(data: dict) -> Book:
    return from_dict(
        data_class=Book,
        data=data,
        config=Config(
            forward_references={"datetime": datetime},
            cast=[tuple, Enum],
            type_hooks={datetime: datetime.fromisoformat},
        ),
    )


def deleted_hash_json_deserializer(data: dict) -> DeletedHash:
    return from_dict(data_class=DeletedHash, data=data)


class RestoreDataUseCase:
    def __init__(
        self,
        book_storage: BooksStorageABC,
        deleted_hash_storage: DeletedHashStorageABC,
        book_deserializer: Callable[[dict], Book] = book_json_deserializer,
        deleted_hash_deserializer: Callable[
            [dict], DeletedHash
        ] = deleted_hash_json_deserializer,
    ) -> None:
        self._book_storage = book_storage
        self._deleted_hash_storage = deleted_hash_storage
        self._book_deserializer = book_deserializer
        self._deleted_hash_deserializer = deleted_hash_deserializer

    async def execute(  # noqa: C901
        self, data: Iterable[bytes]
    ) -> None | InvalidDataError:
        data_iter = iter(data)
        next(data_iter)  # version
        books = []
        deleted_hashes = []
        for i, item in enumerate(data_iter):
            try:
                item_str = item.decode("utf-8")
            except UnicodeDecodeError:
                return InvalidDataError(f"Invalid encoding at line {i + 2}")

            if item_str := item_str.strip():
                try:
                    json_data = json.loads(item_str)
                except json.JSONDecodeError:
                    return InvalidDataError(f"Invalid JSON at line {i + 2}")
                if error := validate_format(json_data):
                    return error

                if json_data["type"] == "book":
                    books.append(self._book_deserializer(json_data))
                elif json_data["type"] == "deleted_hash":
                    deleted_hashes.append(self._deleted_hash_deserializer(json_data))
                else:
                    raise RuntimeError("Unreachable code")
        if books:
            await self._book_storage.extend(books)
        if deleted_hashes:
            await self._deleted_hash_storage.extend(deleted_hashes)
        return None
