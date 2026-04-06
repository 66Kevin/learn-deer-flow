from __future__ import annotations

import os
from typing import Any

from mini_deerflow.config import load_app_config
from mini_deerflow.config.tool_config import ToolConfig
from mini_deerflow.reflection import resolve_object
from mini_deerflow.tools.builtins import get_builtin_tools


def _resolve_env_placeholders(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("$") and len(value) > 1:
        return os.getenv(value[1:], value)
    if isinstance(value, dict):
        return {key: _resolve_env_placeholders(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_resolve_env_placeholders(item) for item in value]
    return value


def _create_configured_tool(tool_config: ToolConfig) -> Any:
    provider = resolve_object(tool_config.use)
    if hasattr(provider, "name") and hasattr(provider, "invoke"):
        return provider
    if not callable(provider):
        raise TypeError(f"Configured tool provider must be callable or a tool object: {tool_config.use}")

    init_kwargs = _resolve_env_placeholders(tool_config.settings)
    tool = provider(name=tool_config.name, **init_kwargs)
    if not hasattr(tool, "name"):
        raise TypeError(f"Configured tool provider did not return a tool-like object: {tool_config.use}")
    return tool


def get_available_tools(
    config_path: str | os.PathLike[str] | None = None,
    groups: list[str] | None = None,
) -> list[Any]:
    """Return builtin and configured tools allowed by config and runtime filters."""

    app_config = load_app_config(config_path)
    configured_groups = {group.name for group in app_config.tool_groups}
    active_groups = configured_groups if groups is None else configured_groups.intersection(groups)

    tools: list[Any] = []
    for group_name, tool in get_builtin_tools():
        if group_name in active_groups:
            tools.append(tool)

    for tool_config in app_config.tools:
        if tool_config.group in active_groups:
            tools.append(_create_configured_tool(tool_config))

    return tools
