from __future__ import annotations

from typing import TYPE_CHECKING

from clippings.web.presenters.book.urls import make_book_urls
from clippings.web.presenters.dtos import UrlDTO, UrlTemplateDTO

if TYPE_CHECKING:
    from collections.abc import Iterator


class UrlsManager:
    def __init__(self, urls: list[UrlTemplateDTO]) -> None:
        check_url_templates(urls)
        self._urls = {url.id: url for url in urls}

    def __iter__(self) -> Iterator[UrlTemplateDTO]:
        return iter(self._urls.values())

    def get_template(self, url_id: str) -> UrlTemplateDTO:
        try:
            return self._urls[url_id]
        except KeyError:
            raise ValueError(f"Unknown URL ID: {url_id}") from None

    def build_url(self, url_id: str, **kwargs: str) -> UrlDTO:
        template = self.get_template(url_id)
        return template.to_url_dto(**kwargs)


def check_url_templates(templates: list[UrlTemplateDTO]) -> None:
    if not templates:
        raise ValueError("No URL templates provided")
    if len(templates) != len({template.id for template in templates}):
        raise ValueError("Duplicate URL template IDs")


urls = [
    UrlTemplateDTO(
        id="home_page",
        template="/",
        method="get",
    ),
    *make_book_urls(),
]
check_url_templates(urls)

urls_manager = UrlsManager(urls)
