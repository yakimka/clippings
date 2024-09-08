from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Literal, TypeAlias, TypeVar

from clippings.web.presenters.html_renderers import not_found_page_renderer

if TYPE_CHECKING:
    from collections.abc import Callable


T = TypeVar("T")


@dataclass
class PresenterResult(Generic[T]):
    data: T
    renderer: Callable[[T], str]
    status: int = 200

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
        return PresenterResult(data, not_found_page_renderer, status=404)


@dataclass
class NotFoundDTO:
    page_title: str
    message: str
    go_to_home_action: ActionDTO


NotFoundPresenterResult: TypeAlias = PresenterResult[NotFoundDTO]


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
