from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clippings.web.presenters.dtos import UrlDTO
    from clippings.web.presenters.urls import UrlsManager


@dataclass
class MenuItem:
    text: str
    url: UrlDTO


@dataclass
class NavMenu:
    title: str
    items: list[MenuItem]


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
            items=[
                MenuItem(
                    text="Reset deleted memory",
                    url=urls_manager.build_url("deleted_hash_clear"),
                ),
                MenuItem(text="Logout", url=urls_manager.build_url("logout")),
            ],
        ),
    )
