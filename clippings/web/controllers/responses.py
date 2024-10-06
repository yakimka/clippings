from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from clippings.web.presenters.book.system_pages import NotFoundDTO

if TYPE_CHECKING:
    from collections.abc import AsyncIterable, Iterable

    from typing_extensions import Self

    from clippings.web.presenters.dtos import PresenterResult


@dataclass(kw_only=True)
class Response:
    payload: Any
    media_type: str | None = None
    status_code: int = 200
    headers: dict[str, str] | None = None

    @classmethod
    def from_presenter_result(cls, presenter_result: PresenterResult) -> Self:
        status_code = 200
        if isinstance(presenter_result.data, NotFoundDTO):
            status_code = 404
        return cls(
            payload=presenter_result.render(),
            status_code=status_code,
        )


@dataclass(kw_only=True)
class HTMLResponse(Response):
    payload: str
    media_type: str = "text/html"


@dataclass(kw_only=True)
class RedirectResponse(Response):
    url: str
    payload: str = ""
    status_code: int = 303


@dataclass(kw_only=True)
class StreamingResponse(Response):
    payload: AsyncIterable[Any] | Iterable[Any]
    status_code: int = 200
