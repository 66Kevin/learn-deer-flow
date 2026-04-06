from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ModelConfig:
    """Minimal model config for P02."""

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
        name = data.get("name")
        use = data.get("use")
        model = data.get("model")
        supports_thinking = data.get("supports_thinking", False)
        supports_vision = data.get("supports_vision", False)

        if not isinstance(name, str) or not name:
            raise ValueError("Model config must define `name`.")
        if not isinstance(use, str) or not use:
            raise ValueError("Model config must define `use`.")
        if not isinstance(model, str) or not model:
            raise ValueError("Model config must define `model`.")
        if not isinstance(supports_thinking, bool):
            raise ValueError("Model config field `supports_thinking` must be a boolean.")
        if not isinstance(supports_vision, bool):
            raise ValueError("Model config field `supports_vision` must be a boolean.")

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
            name=name,
            use=use,
            model=model,
            display_name=data.get("display_name"),
            description=data.get("description"),
            supports_thinking=supports_thinking,
            supports_vision=supports_vision,
            settings=settings,
        )

    def build_init_kwargs(self) -> dict[str, Any]:
        return {"model": self.model, **self.settings}
