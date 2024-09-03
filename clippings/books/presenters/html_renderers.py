from __future__ import annotations

from typing import TYPE_CHECKING, Any

from jinja2 import Environment, PackageLoader, StrictUndefined
from markupsafe import Markup

if TYPE_CHECKING:
    from collections.abc import Callable

    from clippings.books.presenters.dtos import UrlDTO

jinja_env = Environment(
    loader=PackageLoader(__name__, "templates"),
    undefined=StrictUndefined,
    autoescape=True,
)


def hx_link(url: UrlDTO) -> Markup:
    return Markup(f'hx-{url.method}="{url.value}"')


jinja_env.globals.update(hx_link=hx_link)


def make_html_renderer(template_name: str) -> Callable[[Any], str]:
    def render(data: Any) -> str:
        return jinja_env.get_template(template_name).render(data=data)

    return render


not_found_page_renderer = make_html_renderer("404_not_found.jinja2")
