from dataclasses import dataclass
from typing import Literal

from clippings.web.presenters.dtos import UrlDTO


@dataclass(kw_only=True)
class UrlTemplateDTO:
    id: str
    template: str
    method: Literal["get", "post", "put", "patch", "delete"]

    def to_url_dto(self, **kwargs: str) -> UrlDTO:
        return UrlDTO(value=self.template.format(**kwargs), method=self.method)


def make_book_urls(base_url: str = "/books") -> list[UrlTemplateDTO]:
    def make_template(template: str) -> str:
        return f"{base_url.rstrip('/')}{template}"

    templates = [
        UrlTemplateDTO(
            id="book_add",
            template=make_template(""),
            method="post",
        ),
        UrlTemplateDTO(
            id="book_add_form",
            template=make_template("/add"),
            method="post",
        ),
        UrlTemplateDTO(
            id="book_delete",
            template=make_template("/{book_id}"),
            method="delete",
        ),
        UrlTemplateDTO(
            id="book_detail_page",
            template=make_template("/{book_id}"),
            method="get",
        ),
        UrlTemplateDTO(
            id="book_info",
            template=make_template("/{book_id}/info"),
            method="get",
        ),
        UrlTemplateDTO(
            id="book_info_update",
            template=make_template("/{book_id}/info"),
            method="put",
        ),
        UrlTemplateDTO(
            id="book_info_update_form",
            template=make_template("/{book_id}/info/edit"),
            method="get",
        ),
        UrlTemplateDTO(
            id="book_list_page",
            template=make_template(""),
            method="get",
        ),
        UrlTemplateDTO(
            id="book_review",
            template=make_template("/{book_id}/review"),
            method="get",
        ),
        UrlTemplateDTO(
            id="book_review_update",
            template=make_template("/{book_id}/review"),
            method="put",
        ),
        UrlTemplateDTO(
            id="book_review_update_form",
            template=make_template("/{book_id}/review/edit"),
            method="get",
        ),
        UrlTemplateDTO(
            id="clipping_add",
            template=make_template("/{book_id}/clippings"),
            method="post",
        ),
        UrlTemplateDTO(
            id="clipping_add_form",
            template=make_template("/{book_id}/clippings/add"),
            method="get",
        ),
        UrlTemplateDTO(
            id="clipping_delete",
            template=make_template("/{book_id}/clippings/{clipping_id}"),
            method="delete",
        ),
        UrlTemplateDTO(
            id="clipping_detail",
            template=make_template("/{book_id}/clippings/{clipping_id}"),
            method="get",
        ),
        UrlTemplateDTO(
            id="clipping_import_page",
            template=make_template("/import"),
            method="get",
        ),
        UrlTemplateDTO(
            id="clipping_upload",
            template=make_template("/import"),
            method="post",
        ),
        UrlTemplateDTO(
            id="clipping_update",
            template=make_template("/{book_id}/clippings/{clipping_id}"),
            method="put",
        ),
        UrlTemplateDTO(
            id="clipping_update_form",
            template=make_template("/{book_id}/clippings/{clipping_id}/edit"),
            method="get",
        ),
        UrlTemplateDTO(
            id="inline_note_add",
            template=make_template("/{book_id}/clippings/{clipping_id}/inline_notes"),
            method="post",
        ),
        UrlTemplateDTO(
            id="inline_note_add_form",
            template=make_template(
                "/{book_id}/clippings/{clipping_id}/inline_notes/add"
            ),
            method="get",
        ),
        UrlTemplateDTO(
            id="inline_note_delete",
            template=make_template(
                "/{book_id}/clippings/{clipping_id}/inline_notes/{inline_note_id}"
            ),
            method="delete",
        ),
        UrlTemplateDTO(
            id="inline_note_unlink",
            template=make_template(
                "/{book_id}/clippings/{clipping_id}/"
                "inline_notes/{inline_note_id}/unlink"
            ),
            method="post",
        ),
        UrlTemplateDTO(
            id="inline_note_update",
            template=make_template(
                "/{book_id}/clippings/{clipping_id}/inline_notes/{inline_note_id}"
            ),
            method="put",
        ),
        UrlTemplateDTO(
            id="inline_note_update_form",
            template=make_template(
                "/{book_id}/clippings/{clipping_id}/inline_notes/{inline_note_id}/edit"
            ),
            method="get",
        ),
    ]
    check_url_templates(templates)
    return templates


def check_url_templates(templates: list[UrlTemplateDTO]) -> None:
    if not templates:
        raise ValueError("No URL templates provided")
    if len(templates) != len({template.id for template in templates}):
        raise ValueError("Duplicate URL template IDs")


class UrlsManager:
    def __init__(self, urls: list[UrlTemplateDTO]) -> None:
        check_url_templates(urls)
        self._urls = {url.id: url for url in urls}

    def get_template(self, url_id: str) -> UrlTemplateDTO:
        try:
            return self._urls[url_id]
        except KeyError:
            raise ValueError(f"Unknown URL ID: {url_id}") from None

    def build_url(self, url_id: str, **kwargs: str) -> UrlDTO:
        template = self.get_template(url_id)
        return template.to_url_dto(**kwargs)
