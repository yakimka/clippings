import picodi
from starlette.applications import Starlette
from starlette.routing import Route

from clippings.web.presenters.urls import urls_manager
from clippings.web.views import get_views_map


async def startup() -> None:
    await picodi.init_dependencies()
    print("Ready to go")


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


app = Starlette(debug=True, routes=make_routes(), on_startup=[startup])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "clippings.web.app:app",
        host="0.0.0.0",  # noqa: S104
        port=8000,
        reload=True,
        reload_dirs=["/opt/project/clippings/"],
    )
