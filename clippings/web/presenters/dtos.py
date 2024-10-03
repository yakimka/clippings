from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Literal, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable


T = TypeVar("T")


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
    description: str = ""
    confirm_message: str = ""


@dataclass
class PaginationDTO:
    current_page: int
    total_pages: int
    items: list[PaginationItemDTO]


@dataclass
class PaginationItemDTO:
    text: str
    url: str | None


@dataclass(kw_only=True)
class UrlTemplateDTO:
    id: str
    template: str
    method: Literal["get", "post", "put", "patch", "delete"]

    def to_url_dto(self, **kwargs: str) -> UrlDTO:
        return UrlDTO(value=self.template.format(**kwargs), method=self.method)
