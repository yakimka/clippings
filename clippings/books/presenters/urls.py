from dataclasses import dataclass
from typing import Literal

from clippings.books.presenters.dtos import UrlDTO


@dataclass(kw_only=True)
class UrlTemplateDTO:
    id: str
    template: str
    method: Literal["get", "post", "put", "patch", "delete"]

    def to_url_dto(self, **kwargs) -> UrlDTO:
        return UrlDTO(value=self.template.format(**kwargs), method=self.method)


def make_books_urls_builder(base_url: str = "/"):
    def build_books_urls(
        book_list: str = "books",
        book_lookup: str = "{book_id}",
        clipping_list: str = "clippings",
        clipping_lookup: str = "{clipping_id}",
        clipping_unlink_segment: str = "unlink",
        inline_note_list: str = "inline_notes",
        inline_note_lookup: str = "{inline_note_id}",
        info_segment: str = "info",
        review_segment: str = "review",
        add_form_segment: str = "add",
        update_form_segment: str = "edit",
    ):
        book_list_url = f"{base_url.rstrip("/")}/{book_list}"
        book_detail_url = f"{book_list_url}/{book_lookup}"
        clipping_list_url = f"{book_detail_url}/{clipping_list}"
        clipping_detail_url = f"{clipping_list_url}/{clipping_lookup}"
        inline_note_list_url = f"{clipping_detail_url}/{inline_note_list}"
        inline_note_detail_url = f"{inline_note_list_url}/{inline_note_lookup}"
        book_info_url = f"{book_detail_url}/{info_segment}"
        book_review_url = f"{book_detail_url}/{review_segment}"

        templates = [
            UrlTemplateDTO(
                id="book_add_form",
                template=f"{book_list_url}/{add_form_segment}",
                method="post",
            ),
            UrlTemplateDTO(id="book_add", template=book_list_url, method="post"),
            UrlTemplateDTO(id="book_list_page", template=book_list_url, method="get"),
            UrlTemplateDTO(
                id="book_detail_page", template=book_detail_url, method="get"
            ),
            UrlTemplateDTO(id="book_info", template=book_info_url, method="get"),
            UrlTemplateDTO(
                id="book_info_update_form",
                template=f"{book_info_url}/{update_form_segment}",
                method="get",
            ),
            UrlTemplateDTO(id="book_info_update", template=book_info_url, method="put"),
            UrlTemplateDTO(id="book_review", template=book_review_url, method="get"),
            UrlTemplateDTO(
                id="book_review_update_form",
                template=f"{book_review_url}/{update_form_segment}",
                method="get",
            ),
            UrlTemplateDTO(
                id="book_review_update", template=book_review_url, method="put"
            ),
            UrlTemplateDTO(id="book_delete", template=book_detail_url, method="delete"),
            UrlTemplateDTO(
                id="clipping_add_form",
                template=f"{clipping_list_url}/{add_form_segment}",
                method="get",
            ),
            UrlTemplateDTO(
                id="clipping_add", template=clipping_list_url, method="post"
            ),
            UrlTemplateDTO(
                id="clipping_detail", template=clipping_detail_url, method="get"
            ),
            UrlTemplateDTO(
                id="clipping_update_form",
                template=f"{clipping_detail_url}/{update_form_segment}",
                method="get",
            ),
            UrlTemplateDTO(
                id="clipping_update", template=clipping_detail_url, method="put"
            ),
            UrlTemplateDTO(
                id="clipping_delete", template=clipping_detail_url, method="delete"
            ),
            UrlTemplateDTO(
                id="inline_note_add_form",
                template=f"{inline_note_list_url}/{add_form_segment}",
                method="get",
            ),
            UrlTemplateDTO(
                id="inline_note_add", template=inline_note_list_url, method="post"
            ),
            UrlTemplateDTO(
                id="inline_note_update_form",
                template=f"{inline_note_detail_url}/{update_form_segment}",
                method="get",
            ),
            UrlTemplateDTO(
                id="inline_note_update", template=inline_note_detail_url, method="put"
            ),
            UrlTemplateDTO(
                id="inline_note_delete",
                template=inline_note_detail_url,
                method="delete",
            ),
            UrlTemplateDTO(
                id="inline_note_unlink",
                template=f"{inline_note_detail_url}/{clipping_unlink_segment}",
                method="post",
            ),
        ]
        check_url_templates(templates)
        return templates

    return build_books_urls


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

    def build_url(self, url_id: str, **kwargs) -> UrlDTO:
        template = self.get_template(url_id)
        return template.to_url_dto(**kwargs)
