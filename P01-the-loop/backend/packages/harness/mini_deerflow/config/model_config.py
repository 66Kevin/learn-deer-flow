from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ModelConfig:
    """Minimal model config for P01.

    DeerFlow 2.0 uses Pydantic and a richer config schema. For P01 we only keep
    the fields needed to create one chat model instance while preserving the
    same high-level ideas: a stable `name`, a `use` import path, and provider
    settings that stay outside the lead agent loop.
    """

    name: str
    use: str
    model: str
    display_name: str | None = None
    description: str | None = None
    supports_thinking: bool = False
    supports_vision: bool = False
    settings: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelConfig":
        known_fields = {
            "name",
            "use",
            "model",
            "display_name",
            "description",
            "supports_thinking",
            "supports_vision",
        }
        settings = {key: value for key, value in data.items() if key not in known_fields}
        return cls(
            name=str(data["name"]),
            use=str(data["use"]),
            model=str(data["model"]),
            display_name=data.get("display_name"),
            description=data.get("description"),
            supports_thinking=bool(data.get("supports_thinking", False)),
            supports_vision=bool(data.get("supports_vision", False)),
            settings=settings,
        )

    def build_init_kwargs(self) -> dict[str, Any]:
        return {"model": self.model, **self.settings}

