from __future__ import annotations

from typing import TYPE_CHECKING, Any

from jinja2 import Environment, PackageLoader, StrictUndefined
from markupsafe import Markup
from picodi import Provide, inject

from clippings.web.deps import get_request_context
from clippings.web.presenters.global_data import create_global_data
from clippings.web.presenters.urls import urls_manager

if TYPE_CHECKING:
    from collections.abc import Callable

    from clippings.web.presenters.dtos import UrlDTO

jinja_env = Environment(
    loader=PackageLoader(__name__, "templates"),
    undefined=StrictUndefined,
    autoescape=True,
)


def hx_link(url: UrlDTO) -> Markup:
    return Markup(f'hx-{url.method}="{url.value}"')


def split_by_newline(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    return text.split("\n")


jinja_env.globals.update(hx_link=hx_link, split_by_newline=split_by_newline)


def make_html_renderer(template_name: str) -> Callable[[Any], str]:
    @inject
    def render(data: Any, request_context: dict = Provide(get_request_context)) -> str:
        global_data = create_global_data(request_context, urls_manager=urls_manager)
        return jinja_env.get_template(template_name).render(
            data=data, global_data=global_data
        )

    return render


not_found_page_renderer = make_html_renderer("404_not_found.jinja2")
