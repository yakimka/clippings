import importlib
import pkgutil
from collections.abc import Callable
from inspect import isclass
from pathlib import Path


def get_views_map() -> dict[str, Callable]:
    views = {}
    views_path = Path(__file__).parent
    for _, module_name, _ in pkgutil.iter_modules([str(views_path)]):
        module = importlib.import_module(f"{views_path.name}.{module_name}")
        for name in dir(module):
            if name.startswith("_"):
                continue
            obj = getattr(module, name)
            if isclass(obj) or not callable(obj):
                continue

            views[name] = getattr(module, name)

    return views
