from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Protocol

from jinja2 import Environment, PackageLoader, StrictUndefined
from markupsafe import Markup

if TYPE_CHECKING:
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


def not_found_page_renderer(data: Any) -> str:
    return "Not found"
