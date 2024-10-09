from picodi import registry

from clippings.deps import get_default_adapters
from clippings.settings import AdaptersSettings


@registry.override(get_default_adapters)
def get_default_adapters_for_web() -> AdaptersSettings:
    return AdaptersSettings.defaults_for_cli()