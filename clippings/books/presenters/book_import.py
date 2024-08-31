from dataclasses import dataclass

from clippings.books.presenters.dtos import ActionDTO
from clippings.books.presenters.urls import UrlsManager


@dataclass
class ImportPageDTO:
    page_title: str
    import_action: ActionDTO


class ImportPagePresenter:
    def __init__(self, urls_manager: UrlsManager) -> None:
        self._urls_manager = urls_manager

    async def page(self) -> ImportPageDTO:
        return ImportPageDTO(
            page_title="Import clippings",
            import_action=ActionDTO(
                id="import",
                label="Save",
                url=self._urls_manager.build_url("clipping_upload"),
            ),
        )
