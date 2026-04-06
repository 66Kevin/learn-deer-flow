from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ToolGroupConfig:
    """Minimal tool group config for P02."""

    name: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolGroupConfig":
        name = data.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("Tool group config must define a non-empty `name`.")
        return cls(name=name)


@dataclass(slots=True)
class ToolConfig:
    """Minimal configured tool schema for P02."""

    name: str
    group: str
    use: str
    settings: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolConfig":
        name = data.get("name")
        group = data.get("group")
        use = data.get("use")
        if not isinstance(name, str) or not name:
            raise ValueError("Tool config must define `name`.")
        if not isinstance(group, str) or not group:
            raise ValueError("Tool config must define `group`.")
        if not isinstance(use, str) or not use:
            raise ValueError("Tool config must define `use`.")

        known_fields = {"name", "group", "use"}
        settings = {key: value for key, value in data.items() if key not in known_fields}
        return cls(name=name, group=group, use=use, settings=settings)
