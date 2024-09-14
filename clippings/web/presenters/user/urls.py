from clippings.web.presenters.dtos import UrlTemplateDTO


def make_user_urls(base_url: str = "/users") -> list[UrlTemplateDTO]:
    def make_template(template: str) -> str:
        return f"{base_url.rstrip('/')}{template}"

    return [
        UrlTemplateDTO(
            id="login",
            template=make_template("/login"),
            method="get",
        ),
    ]
