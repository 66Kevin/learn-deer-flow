from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class FallbackChatModel:
    """Minimal stand-in used when optional chat model deps are unavailable."""

    model: str
    kwargs: dict[str, Any] = field(default_factory=dict)

    def __init__(self, model: str, **kwargs: Any) -> None:
        self.model = model
        self.kwargs = kwargs


def resolve_object(path: str) -> Any:
    """Resolve an object from `module:attr` or `module.attr` notation."""

    if ":" in path:
        module_name, attribute_name = path.split(":", 1)
    else:
        module_name, _, attribute_name = path.rpartition(".")

    if not module_name or not attribute_name:
        raise ValueError(f"Invalid import path: {path!r}")

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if path == "langchain_openai:ChatOpenAI":
            return FallbackChatModel
        raise exc
    return getattr(module, attribute_name)
