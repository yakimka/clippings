import contextlib
from collections.abc import AsyncGenerator
from pathlib import Path

import picodi
import sentry_sdk
from picodi.integrations.starlette import RequestScopeMiddleware
from sentry_sdk.integrations.starlette import StarletteIntegration
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette_exporter import PrometheusMiddleware, handle_metrics

from clippings.deps import get_infrastructure_settings
from clippings.web.auth import BasicAuthBackend
from clippings.web.middleware import ClosingSlashMiddleware
from clippings.web.presenters.urls import urls_manager
from clippings.web.views import get_views_map
from clippings.web.views.system import not_found_view, server_error_view

CURRENT_DIR = Path(__file__).parent


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncGenerator[None, None]:  # noqa: U100
    await picodi.init_dependencies()
    try:
        yield
    finally:
        await picodi.shutdown_dependencies()  # noqa: ASYNC102


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
    Middleware(PrometheusMiddleware),
]

app = Starlette(
    routes=[
        *make_routes(),
        Route("/metrics/", handle_metrics),
        Mount(
            "/",
            app=StaticFiles(directory=CURRENT_DIR / "presenters" / "public"),
            name="static",
        ),
    ],
    middleware=middleware,
    lifespan=lifespan,
    exception_handlers=exception_handlers,
)

settings = get_infrastructure_settings()

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=0.3,
        profiles_sample_rate=0.3,
        integrations=[StarletteIntegration()],
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "clippings.web.main:app",
        host="0.0.0.0",  # noqa: S104
        port=8000,
        lifespan="on",
        reload=True,
        reload_dirs=["/opt/project/clippings/"],
    )
