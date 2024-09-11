from __future__ import annotations

import importlib
import pkgutil
from inspect import isclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def get_views_map() -> dict[str, Callable]:
    views = {}
    views_path = Path(__file__).parent
    for _, module_name, _ in pkgutil.iter_modules([str(views_path)]):
        if module_name.startswith("_"):
            continue
        module = importlib.import_module(
            f"clippings.web.{views_path.name}.{module_name}"
        )
        for name in dir(module):
            if name.startswith("_"):
                continue
            obj = getattr(module, name)
            if isclass(obj) or not callable(obj):
                continue

            views[name] = getattr(module, name)

    return views
