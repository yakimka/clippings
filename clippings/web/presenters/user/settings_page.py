from __future__ import annotations

from dataclasses import dataclass

from clippings.web.presenters.dtos import ActionDTO, PresenterResult
from clippings.web.presenters.html_renderers import make_html_renderer
from clippings.web.presenters.urls import urls_manager


@dataclass
class SettingsPageDTO:
    page_title: str
    actions: list[ActionDTO]


class SettingsPagePresenter:
    async def present(self) -> PresenterResult[SettingsPageDTO]:
        data = SettingsPageDTO(
            page_title="Settings",
            actions=[
                ActionDTO(
                    id="reset_deleted_memory",
                    label="Reset deleted memory",
                    url=urls_manager.build_url("deleted_hash_clear"),
                    description=(
                        "When you delete your clippings, we save a hash for each "
                        "removed item. This helps us prevent reimporting clippings "
                        "that you've already deleted. Resetting this memory will allow "
                        "those clippings to be imported again, even if they were "
                        "previously deleted."
                    ),
                    confirm_message=(
                        "Are you sure you want to reset your deleted memory? "
                        "This action cannot be undone."
                    ),
                ),
            ],
        )
        return PresenterResult(
            data=data, renderer=make_html_renderer("user/settings_page.jinja2")
        )
