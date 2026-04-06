from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mini_deerflow.config.model_config import ModelConfig


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[4]


def get_default_config_path() -> Path:
    backend_root = _backend_root()
    config_path = backend_root / "config.yaml"
    if config_path.exists():
        return config_path
    return backend_root / "config.example.yaml"


def _load_config_payload(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")

    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None

    if yaml is not None:
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)

    if not isinstance(data, dict):
        raise ValueError(f"Config file {path} must contain a mapping at the top level.")
    return data


@dataclass(slots=True)
class AppConfig:
    models: list[ModelConfig]
    source_path: Path

    @classmethod
    def from_dict(cls, data: dict[str, Any], source_path: Path) -> "AppConfig":
        raw_models = data.get("models", [])
        if not isinstance(raw_models, list) or not raw_models:
            raise ValueError("Config must define at least one model in `models`.")
        return cls(
            models=[ModelConfig.from_dict(model) for model in raw_models],
            source_path=source_path,
        )

    def get_model_config(self, name: str) -> ModelConfig | None:
        for model in self.models:
            if model.name == name:
                return model
        return None


def load_app_config(path: str | os.PathLike[str] | None = None) -> AppConfig:
    config_path = Path(path) if path is not None else get_default_config_path()
    payload = _load_config_payload(config_path)
    return AppConfig.from_dict(payload, source_path=config_path)
