from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clippings.web.presenters.dtos import ActionDTO, PresenterResult
from clippings.web.presenters.html_renderers import make_html_renderer

if TYPE_CHECKING:
    from clippings.books.use_cases.import_clippings import ImportedBookDTO
    from clippings.web.presenters.urls import UrlsManager


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


@dataclass
class ImportResultDTO:
    title: str
    is_empty: bool
    empty_message: str
    items: list[ImportResultItemDTO]


@dataclass
class ImportResultItemDTO:
    book_name: str
    import_result: str
    new_label: str | None


class ImportClippingsResultPresenter:
    async def present(
        self, statistics: list[ImportedBookDTO]
    ) -> PresenterResult[ImportResultDTO]:
        return PresenterResult(
            data=ImportResultDTO(
                title="Import result",
                is_empty=not bool(statistics),
                empty_message="No clippings were imported",
                items=[
                    ImportResultItemDTO(
                        book_name=f"{item.title} by {item.authors}",
                        import_result=(
                            f"Imported {item.imported_clippings_count} clippings"
                        ),
                        new_label="[NEW]" if item.is_new else None,
                    )
                    for item in statistics
                ],
            ),
            renderer=make_html_renderer("book/clippings_import_result.jinja2"),
        )
