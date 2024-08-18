from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class UrlTemplateDTO:
    template: str
    method: Literal["get", "post", "put", "delete"] = "get"


@dataclass
class UrlDTO:
    value: str
    method: Literal["get", "post", "put", "delete"] = "get"

    @classmethod
    def from_template(cls, template: UrlTemplateDTO, **kwargs: Any) -> UrlDTO:
        return cls(value=template.template.format(**kwargs), method=template.method)


@dataclass
class ActionDTO:
    id: str
    label: str
    url: UrlDTO


@dataclass
class PaginationItemDTO:
    text: str
    url: str | None


@dataclass
class NotFoundDTO:
    page_title: str
    message: str
