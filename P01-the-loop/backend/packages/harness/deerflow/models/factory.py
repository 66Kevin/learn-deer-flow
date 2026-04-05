from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from deerflow.config import load_app_config
from deerflow.reflection import resolve_object


def _resolve_env_placeholders(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("$") and len(value) > 1:
        return os.getenv(value[1:], value)
    if isinstance(value, dict):
        return {key: _resolve_env_placeholders(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_resolve_env_placeholders(item) for item in value]
    return value


def create_chat_model(
    name: str | None = None,
    config_path: str | os.PathLike[str] | None = None,
    **overrides: Any,
) -> Any:
    """Create a chat model instance from the configured model list.

    The implementation stays intentionally small in P01:
    - load config
    - pick the requested model or the first configured model
    - resolve the provider class dynamically
    - instantiate it with config-driven settings
    """

    app_config = load_app_config(config_path)
    selected = app_config.models[0] if name is None else app_config.get_model_config(name)
    if selected is None:
        raise ValueError(f"Model {name!r} not found in config {Path(app_config.source_path)}")

    model_class = resolve_object(selected.use)
    init_kwargs = _resolve_env_placeholders(selected.build_init_kwargs())
    init_kwargs.update(overrides)
    return model_class(**init_kwargs)

