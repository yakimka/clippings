from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, Literal, TypeVar

from clippings.books.presenters.html_renderers import not_found_page_renderer

T: TypeVar = TypeVar("T")


@dataclass
class PresenterResult(Generic[T]):
    data: T
    renderer: Callable[[T], str]

    def render(self) -> str:
        return self.renderer(self.data)

    @classmethod
    def not_found(cls) -> NotFoundPresenterResult:
        data = NotFoundDTO(
            page_title="Not Found",
            message="Sorry, the page you are looking for does not exist.",
            go_to_home_action=ActionDTO(
                id="go_to_home",
                label="Go to the home page",
                url=UrlDTO(value="/"),
            ),
        )
        return cls(data, not_found_page_renderer)


@dataclass
class NotFoundDTO:
    page_title: str
    message: str
    go_to_home_action: ActionDTO


NotFoundPresenterResult = PresenterResult[NotFoundDTO]


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
