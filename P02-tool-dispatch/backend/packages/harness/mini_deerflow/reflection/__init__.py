from __future__ import annotations

import importlib
from typing import Any


def resolve_object(path: str) -> Any:
    """Resolve an object from `module:attr` or `module.attr` notation."""

    if ":" in path:
        module_name, attribute_name = path.split(":", 1)
    else:
        module_name, _, attribute_name = path.rpartition(".")

    if not module_name or not attribute_name:
        raise ValueError(f"Invalid import path: {path!r}")

    module = importlib.import_module(module_name)
    return getattr(module, attribute_name)
