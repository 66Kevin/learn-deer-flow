from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mini_deerflow.config.model_config import ModelConfig
from mini_deerflow.config.tool_config import ToolConfig, ToolGroupConfig

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised only in minimal local envs
    yaml = None


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[4]


def get_default_config_path() -> Path:
    backend_root = _backend_root()
    config_path = backend_root / "config.yaml"
    if config_path.exists():
        return config_path
    return backend_root / "config.example.yaml"


def _parse_scalar(value: str) -> Any:
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None", "~"}:
        return None
    if value and value.lstrip("-").isdigit():
        return int(value)
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def _simple_yaml_load(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    current_list_name: str | None = None
    current_item: dict[str, Any] | None = None
    current_nested_list_name: str | None = None
    lines = text.splitlines()

    for raw_line in lines:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0 and line.endswith(":"):
            current_list_name = line[:-1]
            root[current_list_name] = []
            current_item = None
            current_nested_list_name = None
            continue

        if indent == 2 and line.startswith("- "):
            if current_list_name is None:
                raise ValueError("Invalid YAML structure: list item without a parent key.")
            current_item = {}
            root[current_list_name].append(current_item)
            current_nested_list_name = None
            line = line[2:]
            if line:
                key, _, value = line.partition(":")
                current_item[key.strip()] = _parse_scalar(value.strip())
            continue

        if indent == 4 and current_item is not None:
            if line.endswith(":"):
                current_nested_list_name = line[:-1]
                current_item[current_nested_list_name] = []
            else:
                key, _, value = line.partition(":")
                current_item[key.strip()] = _parse_scalar(value.strip())
                current_nested_list_name = None
            continue

        if indent == 6 and line.startswith("- ") and current_item is not None and current_nested_list_name is not None:
            current_item[current_nested_list_name].append(_parse_scalar(line[2:].strip()))
            continue

        raise ValueError(f"Unsupported YAML structure in fallback parser: {raw_line!r}")

    return root


def _load_config_payload(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) if yaml is not None else _simple_yaml_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"Config file {path} must contain a mapping at the top level.")
    return data


@dataclass(slots=True)
class AppConfig:
    """Application config container for the P02 harness."""

    models: list[ModelConfig]
    tool_groups: list[ToolGroupConfig]
    tools: list[ToolConfig]
    source_path: Path

    @classmethod
    def from_dict(cls, data: dict[str, Any], source_path: Path) -> "AppConfig":
        raw_models = data.get("models", [])
        if not isinstance(raw_models, list) or not raw_models:
            raise ValueError("Config must define at least one model in `models`.")

        raw_tool_groups = data.get("tool_groups", [])
        if not isinstance(raw_tool_groups, list) or not raw_tool_groups:
            raise ValueError("Config must define at least one tool group in `tool_groups`.")

        raw_tools = data.get("tools", [])
        if not isinstance(raw_tools, list):
            raise ValueError("Config field `tools` must be a list.")

        models = [ModelConfig.from_dict(model) for model in raw_models]
        tool_groups = [ToolGroupConfig.from_dict(group) for group in raw_tool_groups]
        tools = [ToolConfig.from_dict(tool) for tool in raw_tools]

        group_names = {group.name for group in tool_groups}
        unknown_groups = sorted({tool.group for tool in tools if tool.group not in group_names})
        if unknown_groups:
            joined = ", ".join(unknown_groups)
            raise ValueError(f"Unknown tool group referenced by `tools`: {joined}")

        return cls(models=models, tool_groups=tool_groups, tools=tools, source_path=source_path)

    def get_model_config(self, name: str) -> ModelConfig | None:
        for model in self.models:
            if model.name == name:
                return model
        return None


def load_app_config(path: str | os.PathLike[str] | None = None) -> AppConfig:
    """Load the application config from a YAML file."""

    config_path = Path(path) if path is not None else get_default_config_path()
    payload = _load_config_payload(config_path)
    return AppConfig.from_dict(payload, source_path=config_path)
