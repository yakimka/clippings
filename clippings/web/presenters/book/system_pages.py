from dataclasses import dataclass

from clippings.web.presenters.dtos import ActionDTO, PresenterResult, UrlDTO
from clippings.web.presenters.html_renderers import make_html_renderer


@dataclass
class NotFoundDTO:
    page_title: str
    message: str
    go_to_home_action: ActionDTO


def not_found_page_presenter() -> PresenterResult[NotFoundDTO]:
    data = NotFoundDTO(
        page_title="Not Found",
        message="Sorry, the page you are looking for does not exist.",
        go_to_home_action=ActionDTO(
            id="go_to_home",
            label="Go to the home page",
            url=UrlDTO(value="/"),
        ),
    )
    return PresenterResult(data, make_html_renderer("404_not_found.jinja2"))


@dataclass
class ServerErrorDTO:
    page_title: str
    message: str


def server_error_page_presenter() -> PresenterResult[ServerErrorDTO]:
    data = ServerErrorDTO(
        page_title="Server Error",
        message="Oops, something went wrong on our side. Please try again later.",
    )
    return PresenterResult(data, make_html_renderer("500_server_error.jinja2"))
