from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clippings.web.presenters.dtos import ActionDTO, PresenterResult
from clippings.web.presenters.html_renderers import make_html_renderer

if TYPE_CHECKING:
    from clippings.web.presenters.book.urls import UrlsManager


@dataclass
class ImportPageDTO:
    page_title: str
    import_action: ActionDTO


class ClippingsImportPagePresenter:
    def __init__(self, urls_manager: UrlsManager) -> None:
        self._urls_manager = urls_manager

    async def present(self) -> PresenterResult[ImportPageDTO]:
        data = ImportPageDTO(
            page_title="Import clippings",
            import_action=ActionDTO(
                id="import",
                label="Save",
                url=self._urls_manager.build_url("clipping_upload"),
            ),
        )
        return PresenterResult(
            data=data,
            renderer=make_html_renderer("book/clippings_import_page.jinja2"),
        )
