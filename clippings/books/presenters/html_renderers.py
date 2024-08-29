from typing import Any, Protocol

from jinja2 import Environment, PackageLoader, StrictUndefined
from markupsafe import Markup

from clippings.books.presenters.dtos import UrlDTO

jinja_env = Environment(
    loader=PackageLoader(__name__, "templates"),
    undefined=StrictUndefined,
    autoescape=True,
)


def hx_link(url: UrlDTO) -> Markup:
    return Markup(f'hx-{url.method}="{url.value}"')


jinja_env.globals.update(hx_link=hx_link)


class HtmlRenderer(Protocol):
    def __call__(self, data: Any) -> str:
        pass


def make_jinja_renderer(template_name: str) -> HtmlRenderer:
    def render(data: Any) -> str:
        return jinja_env.get_template(template_name).render(data=data)

    return render


book_list = make_jinja_renderer("books_page.jinja2")
book_detail = make_jinja_renderer("books_detail/page.jinja2")
book_review = make_jinja_renderer("books_detail/review.jinja2")
book_review_update_form = make_jinja_renderer("books_detail/edit_review_form.jinja2")
book_info = make_jinja_renderer("books_detail/book_info.jinja2")
book_info_update_form = make_jinja_renderer("books_detail/edit_book_info_form.jinja2")
