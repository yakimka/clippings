from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, Literal, TypeVar

T: TypeVar = TypeVar("T")


@dataclass
class PresenterResult(Generic[T]):
    data: T
    renderer: Callable[[T], str]

    def render(self) -> str:
        return self.renderer(self.data)


@dataclass
class UrlDTO:
    value: str
    method: Literal["get", "post", "put", "patch", "delete"] = "get"


@dataclass
class ActionDTO:
    id: str
    label: str
    url: UrlDTO | None


@dataclass
class PaginationItemDTO:
    text: str
    url: str | None


@dataclass
class NotFoundDTO:
    page_title: str
    message: str
