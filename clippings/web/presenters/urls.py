from __future__ import annotations

from typing import TYPE_CHECKING

from clippings.web.presenters.book.urls import make_book_urls
from clippings.web.presenters.dtos import UrlDTO, UrlTemplateDTO
from clippings.web.presenters.user.urls import make_user_urls

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


class UrlsManager:
    def __init__(self) -> None:
        self._urls: list[UrlTemplateDTO] = []
        self._tags_to_ids: dict[str, set[str]] = {}

    def __iter__(self) -> Iterator[UrlTemplateDTO]:
        return iter(self._urls)

    def check(self) -> None:
        if not self._urls:
            raise ValueError("No URL templates provided")
        if len(self._urls) != len({template.id for template in self._urls}):
            raise ValueError("Duplicate URL template IDs")

    def add_urls(self, urls: list[UrlTemplateDTO], tags: Iterable[str] = ()) -> None:
        self._urls.extend(urls)
        for tag in tags:
            self._tags_to_ids.setdefault(tag, set()).update({url.id for url in urls})

    def get_by_tag(self, tag: str) -> list[UrlTemplateDTO]:
        if tag not in self._tags_to_ids:
            raise ValueError(f"Unknown tag: {tag}")
        urls = [
            (i, url)
            for i, url in enumerate(self._urls)
            if url.id in self._tags_to_ids[tag]
        ]
        return [url for _, url in sorted(urls)]

    def get_template(self, url_id: str) -> UrlTemplateDTO:
        for url in self._urls:
            if url.id == url_id:
                return url
        raise ValueError(f"Unknown URL ID: {url_id}") from None

    def build_url(self, url_id: str, **kwargs: str) -> UrlDTO:
        template = self.get_template(url_id)
        return template.to_url_dto(**kwargs)


urls_manager = UrlsManager()
urls_manager.add_urls(
    [
        UrlTemplateDTO(
            id="home_page",
            template="/",
            method="get",
        )
    ]
)
urls_manager.add_urls(make_book_urls(), tags=["book"])
urls_manager.add_urls(make_user_urls(), tags=["user"])
urls_manager.check()
