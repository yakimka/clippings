from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clippings.web.presenters.dtos import ActionDTO, UrlDTO

if TYPE_CHECKING:
    from clippings.web.presenters.urls import UrlsManager


@dataclass
class MenuItem:
    text: str
    url: UrlDTO


@dataclass
class NavMenu:
    title: str
    actions: list[ActionDTO]


@dataclass
class GlobalData:
    home_link_text: str
    home_link_url: str
    nav_menu: NavMenu


def create_global_data(request_context: dict, urls_manager: UrlsManager) -> GlobalData:
    return GlobalData(
        home_link_text="Clippings",
        home_link_url="/",
        nav_menu=NavMenu(
            title=request_context.get("user_nickname", "Username"),
            actions=[
                ActionDTO(
                    id="goto_import_page",
                    label="Import clippings",
                    url=urls_manager.build_url("clippings_import_page"),
                ),
                ActionDTO(
                    id="goto_settings_page",
                    label="Settings",
                    url=urls_manager.build_url("settings_page"),
                ),
                ActionDTO(
                    id="logout", label="Logout", url=urls_manager.build_url("logout")
                ),
            ],
        ),
    )
