from __future__ import annotations

from dataclasses import dataclass

from clippings.web.presenters.dtos import PresenterResult
from clippings.web.presenters.html_renderers import make_html_renderer


@dataclass
class SettingsPageDTO:
    page_title: str


class SettingsPagePresenter:
    async def present(self) -> PresenterResult[SettingsPageDTO]:
        data = SettingsPageDTO(page_title="Settings")
        return PresenterResult(
            data=data, renderer=make_html_renderer("user/settings_page.jinja2")
        )
