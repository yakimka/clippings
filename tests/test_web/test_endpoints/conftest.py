import pytest
from httpx import AsyncClient
from picodi import registry
from picodi.helpers import enter, lifespan

from clippings.deps import get_books_storage, get_password_hasher, get_users_map
from clippings.web.deps import get_user_id
from clippings.web.main import app


@pytest.fixture()
def asgi_app():
    return app


@pytest.fixture()
async def client(asgi_app, client_auth) -> AsyncClient:
    async with AsyncClient(
        app=asgi_app, base_url="http://testserver", auth=client_auth, timeout=2
    ) as client:
        yield client


@pytest.fixture(autouse=True)
async def _dependencies_lifespan():
    async with lifespan.async_():
        yield


@pytest.fixture(autouse=True)
async def _override_deps(mother):
    with enter(get_password_hasher) as password_hasher:
        test_user = mother.user(
            id="user:id",
            nickname="testuser",
            hashed_password=password_hasher.hash("testpass"),
        )
    users_map = {"user:id": test_user}

    with registry.override(get_users_map, lambda: users_map):
        yield


@pytest.fixture()
async def book_storage():
    with registry.override(get_user_id, lambda: "user:id"):
        async with enter(get_books_storage) as storage:
            return storage
