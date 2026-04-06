from __future__ import annotations

from mini_deerflow.tools.builtins.current_time import current_time_tool
from mini_deerflow.tools.builtins.echo import echo_tool


def get_builtin_tools() -> list[tuple[str, object]]:
    return [
        ("builtin", current_time_tool),
        ("builtin", echo_tool),
    ]


__all__ = ["get_builtin_tools", "current_time_tool", "echo_tool"]
