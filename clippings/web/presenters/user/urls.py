from clippings.web.presenters.dtos import UrlTemplateDTO


def make_user_urls(base_url: str = "/users") -> list[UrlTemplateDTO]:
    def make_template(template: str, *, add_closing_slash: bool = True) -> str:
        template = template.removesuffix("/")
        if add_closing_slash:
            template = f"{template}/"
        return f"{base_url.rstrip('/')}{template}"

    return [
        UrlTemplateDTO(
            id="logout",
            template=make_template("/logout"),
            method="get",
        ),
        UrlTemplateDTO(
            id="settings_page",
            template=make_template("/me/settings"),
            method="get",
        ),
    ]
