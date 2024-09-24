import pytest

from clippings.web.settings import settings


@pytest.fixture(scope="session", autouse=True)
def _set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
