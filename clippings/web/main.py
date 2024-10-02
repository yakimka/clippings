from pathlib import Path

import picodi
from picodi.integrations.starlette import RequestScopeMiddleware
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from clippings.web.auth import BasicAuthBackend
from clippings.web.middleware import ClosingSlashMiddleware
from clippings.web.presenters.urls import urls_manager
from clippings.web.views import get_views_map
from clippings.web.views.system import not_found_view, server_error_view

CURRENT_DIR = Path(__file__).parent


async def startup() -> None:
    await picodi.init_dependencies()


def make_routes() -> list[Route]:
    views_map = get_views_map()
    result = []
    not_found = set()
    for url_template in urls_manager:
        view = views_map.get(url_template.id)
        if view is None:
            not_found.add(url_template.id)
            continue
        result.append(Route(url_template.template, view, methods=[url_template.method]))

    if not_found:
        raise RuntimeError(f"Views not found: {not_found}")
    return result


exception_handlers = {
    404: not_found_view,
    500: server_error_view,
}

middleware = [
    Middleware(RequestScopeMiddleware),
    Middleware(AuthenticationMiddleware, backend=BasicAuthBackend()),
    Middleware(ClosingSlashMiddleware),
]

app = Starlette(
    routes=[
        *make_routes(),
        Mount(
            "/",
            app=StaticFiles(directory=CURRENT_DIR / "presenters" / "public"),
            name="static",
        ),
    ],
    middleware=middleware,
    on_startup=[startup],
    exception_handlers=exception_handlers,
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "clippings.web.main:app",
        host="0.0.0.0",  # noqa: S104
        port=8000,
        reload=True,
        reload_dirs=["/opt/project/clippings/"],
    )
