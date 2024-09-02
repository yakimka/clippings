from dataclasses import dataclass

from clippings.books.presenters.dtos import ActionDTO, PresenterResult
from clippings.books.presenters.html_renderers import make_html_renderer
from clippings.books.presenters.urls import UrlsManager


@dataclass
class ImportPageDTO:
    page_title: str
    import_action: ActionDTO


class ClippingsImportPagePresenter:
    def __init__(
        self,
        urls_manager: UrlsManager,
        html_template: str = "clippings_import_page.jinja2",
    ) -> None:
        self._urls_manager = urls_manager
        self._renderer = make_html_renderer(html_template)

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
            renderer=self._renderer,
        )
