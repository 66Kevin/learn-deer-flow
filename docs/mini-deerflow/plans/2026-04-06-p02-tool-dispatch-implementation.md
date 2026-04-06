# P02 Tool Dispatch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an isolated `P02-tool-dispatch` stage that keeps the `P01` loop small while adding YAML-backed tool configuration, a unified `get_available_tools()` registry, and a working `tool_call -> tool_result -> final_answer` graph.

**Architecture:** `P02-tool-dispatch` will mirror the `P01-the-loop` stage layout but expand the backend with `tool_groups`, `tools`, builtin tool modules, and one configured community stub tool. The lead agent stays thin by creating one bound model plus a `ToolNode`, while configuration loading and tool instantiation stay in `config/` and `tools/`.

**Tech Stack:** Python 3.12+, `langchain`, `langgraph`, `langchain-openai`, `langchain-core`, `pyyaml`, `pytest`

---

## File Map

- `P02-tool-dispatch/backend/langgraph.json` — register the `lead_agent` graph entrypoint under the `mini_deerflow` namespace.
- `P02-tool-dispatch/backend/config.example.yaml` — real YAML example showing one model, `tool_groups`, and one configured tool.
- `P02-tool-dispatch/backend/packages/harness/mini_deerflow/config/model_config.py` — keep the P01 model schema and provider kwargs handling.
- `P02-tool-dispatch/backend/packages/harness/mini_deerflow/config/tool_config.py` — define `ToolGroupConfig` and `ToolConfig`.
- `P02-tool-dispatch/backend/packages/harness/mini_deerflow/config/app_config.py` — load YAML, validate groups, and expose `models`, `tool_groups`, and `tools`.
- `P02-tool-dispatch/backend/packages/harness/mini_deerflow/models/factory.py` — create chat models from config and resolve env placeholders for provider kwargs.
- `P02-tool-dispatch/backend/packages/harness/mini_deerflow/models/testing.py` — deterministic local model used by tests to emit tool calls and summarize tool outputs.
- `P02-tool-dispatch/backend/packages/harness/mini_deerflow/tools/builtins/current_time.py` — builtin time tool.
- `P02-tool-dispatch/backend/packages/harness/mini_deerflow/tools/builtins/echo.py` — builtin echo tool.
- `P02-tool-dispatch/backend/packages/harness/mini_deerflow/community/stub_search/tools.py` — configured stub tool factory used to prove dynamic loading.
- `P02-tool-dispatch/backend/packages/harness/mini_deerflow/tools/tools.py` — implement `get_available_tools()` and tool filtering.
- `P02-tool-dispatch/backend/packages/harness/mini_deerflow/agents/lead_agent/agent.py` — minimal `call_model -> run_tools -> call_model` graph.
- `tests/p02_tool_dispatch/support.py` — add the P02 harness path to `sys.path`.
- `tests/p02_tool_dispatch/test_layout.py` — verify the stage shape and namespace entrypoint.
- `tests/p02_tool_dispatch/test_tool_config.py` — verify YAML config loading and validation.
- `tests/p02_tool_dispatch/test_tool_registry.py` — verify builtin/configured tool loading and group filtering.
- `tests/p02_tool_dispatch/test_lead_agent.py` — verify the dispatch loop.
- `tests/p02_tool_dispatch/test_readme.py` — verify user-facing documentation stays accurate.
- `tests/p02_tool_dispatch/test_example_config.py` — verify the example config can instantiate its default model.
- `tests/fixtures/p02-config.yaml` — deterministic fixture for unit tests.
- `tests/fixtures/p02-invalid-group.yaml` — fixture proving unknown group validation fails clearly.
- `tests/fixtures/p02-missing-tool-use.yaml` — fixture proving missing `use` fails clearly.

### Task 1: Scaffold the isolated P02 stage project

**Files:**
- Create: `P02-tool-dispatch/README.md`
- Create: `P02-tool-dispatch/backend/pyproject.toml`
- Create: `P02-tool-dispatch/backend/langgraph.json`
- Create: `P02-tool-dispatch/backend/config.example.yaml`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/__init__.py`
- Create: `tests/p02_tool_dispatch/__init__.py`
- Create: `tests/p02_tool_dispatch/support.py`
- Create: `tests/p02_tool_dispatch/test_layout.py`

- [ ] **Step 1: Write the failing test**

```python
from __future__ import annotations

import unittest

from tests.p02_tool_dispatch.support import P02_BACKEND_ROOT


class TestP02Layout(unittest.TestCase):
    def test_stage_layout_has_tool_dispatch_entrypoints(self) -> None:
        self.assertTrue((P02_BACKEND_ROOT / "langgraph.json").exists())
        self.assertTrue((P02_BACKEND_ROOT / "pyproject.toml").exists())
        self.assertTrue((P02_BACKEND_ROOT / "config.example.yaml").exists())
        self.assertTrue((P02_BACKEND_ROOT / "packages" / "harness" / "mini_deerflow").exists())

    def test_langgraph_entry_uses_mini_deerflow_namespace(self) -> None:
        langgraph_config = (P02_BACKEND_ROOT / "langgraph.json").read_text(encoding="utf-8")
        self.assertIn("mini_deerflow.agents:make_lead_agent", langgraph_config)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/p02_tool_dispatch/test_layout.py -v`
Expected: FAIL because `P02-tool-dispatch/` and the required backend files do not exist yet

- [ ] **Step 3: Write minimal implementation**

Create the isolated stage root and the minimal backend metadata files:

```toml
[project]
name = "mini-deerflow-p02"
version = "0.1.0"
description = "mini-deerflow stage P02: Tool Dispatch"
requires-python = ">=3.12"
dependencies = [
    "debugpy>=1.8.0",
    "langchain>=1.2.3",
    "langchain-openai>=1.1.7",
    "langchain-core>=1.1.0",
    "langgraph>=1.0.6,<1.0.10",
    "langgraph-cli[inmem]>=0.4.0,<0.5.0",
    "pyyaml>=6.0.3",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["packages/harness/mini_deerflow"]
```

```json
{
  "$schema": "https://langgra.ph/schema.json",
  "python_version": "3.12",
  "dependencies": ["."],
  "graphs": {
    "lead_agent": "mini_deerflow.agents:make_lead_agent"
  }
}
```

```yaml
models:
  - name: deepseek-v3
    display_name: DeepSeek V3 (Thinking)
    use: langchain_openai:ChatOpenAI
    model: deepseek-reasoner
    base_url: https://api.deepseek.com
    api_key: $DEEPSEEK_API_KEY

tool_groups:
  - name: builtin
  - name: web

tools:
  - name: search_stub
    group: web
    use: mini_deerflow.community.stub_search.tools:search_stub_tool
    results:
      - Mini DeerFlow P02 search result
```

```python
"""mini-deerflow P02 package."""
```

```python
"""Tests for the P02 tool dispatch stage."""
```

```python
from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
P02_ROOT = REPO_ROOT / "P02-tool-dispatch"
P02_BACKEND_ROOT = P02_ROOT / "backend"
P02_HARNESS_ROOT = P02_BACKEND_ROOT / "packages" / "harness"


def ensure_p02_harness_on_path() -> None:
    harness_path = str(P02_HARNESS_ROOT)
    if harness_path not in sys.path:
        sys.path.insert(0, harness_path)
```

```markdown
# P02 Tool Dispatch

`P02-tool-dispatch` 是 `mini-deerflow` 的第二阶段代码实现。

这一阶段会在 `P01-the-loop` 的最小 graph 基础上加入最小 tool dispatch loop：

- `get_available_tools()`
- builtin tools
- configured tools
- `model -> tools -> model`
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/p02_tool_dispatch/test_layout.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add P02-tool-dispatch tests/p02_tool_dispatch
git commit -m "feat: scaffold P02 tool dispatch stage"
```

### Task 2: Add YAML config loading, tool schema validation, and model factory foundations

**Files:**
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/config/__init__.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/config/model_config.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/config/tool_config.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/config/app_config.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/reflection/__init__.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/models/__init__.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/models/factory.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/models/testing.py`
- Create: `tests/fixtures/p02-config.yaml`
- Create: `tests/fixtures/p02-invalid-group.yaml`
- Create: `tests/fixtures/p02-missing-tool-use.yaml`
- Create: `tests/p02_tool_dispatch/test_tool_config.py`
- Create: `tests/p02_tool_dispatch/test_example_config.py`

- [ ] **Step 1: Write the failing tests**

```python
from __future__ import annotations

import unittest

from tests.p02_tool_dispatch.support import REPO_ROOT, ensure_p02_harness_on_path

ensure_p02_harness_on_path()

from mini_deerflow.config import load_app_config  # type: ignore  # noqa: E402
from mini_deerflow.models.factory import create_chat_model  # type: ignore  # noqa: E402


class TestP02ToolConfig(unittest.TestCase):
    def setUp(self) -> None:
        fixtures_root = REPO_ROOT / "tests" / "fixtures"
        self.config_path = fixtures_root / "p02-config.yaml"
        self.invalid_group_path = fixtures_root / "p02-invalid-group.yaml"
        self.missing_use_path = fixtures_root / "p02-missing-tool-use.yaml"

    def test_load_app_config_reads_tool_groups_and_tools(self) -> None:
        config = load_app_config(self.config_path)
        self.assertEqual([group.name for group in config.tool_groups], ["builtin", "web"])
        self.assertEqual(config.tools[0].name, "search_stub")
        self.assertEqual(config.tools[0].group, "web")

    def test_load_app_config_rejects_unknown_tool_group(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown tool group"):
            load_app_config(self.invalid_group_path)

    def test_load_app_config_rejects_tool_without_use(self) -> None:
        with self.assertRaisesRegex(ValueError, "Tool config must define `use`"):
            load_app_config(self.missing_use_path)

    def test_create_chat_model_uses_default_tool_model(self) -> None:
        model = create_chat_model(config_path=self.config_path)
        self.assertEqual(model.__class__.__name__, "ToolCallingChatModel")


if __name__ == "__main__":
    unittest.main()
```

```python
from __future__ import annotations

import os
import unittest

from tests.p02_tool_dispatch.support import P02_BACKEND_ROOT, ensure_p02_harness_on_path

ensure_p02_harness_on_path()

from mini_deerflow.models.factory import create_chat_model  # type: ignore  # noqa: E402


class TestP02ExampleConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.config_path = P02_BACKEND_ROOT / "config.example.yaml"
        self.original_api_key = os.environ.get("DEEPSEEK_API_KEY")
        os.environ["DEEPSEEK_API_KEY"] = "test-key"

    def tearDown(self) -> None:
        if self.original_api_key is None:
            os.environ.pop("DEEPSEEK_API_KEY", None)
        else:
            os.environ["DEEPSEEK_API_KEY"] = self.original_api_key

    def test_example_config_can_create_default_chat_model(self) -> None:
        model = create_chat_model(config_path=self.config_path)
        self.assertIsNotNone(model)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/p02_tool_dispatch/test_tool_config.py tests/p02_tool_dispatch/test_example_config.py -v`
Expected: FAIL because the P02 config modules, model factory, and fixture files do not exist yet

- [ ] **Step 3: Write minimal implementation**

Implement the YAML-backed config models, reflection helper, model factory, and deterministic local test model:

```python
from __future__ import annotations

from mini_deerflow.config.app_config import AppConfig, get_default_config_path, load_app_config

__all__ = ["AppConfig", "get_default_config_path", "load_app_config"]
```

```python
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
```

```python
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
```

```python
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from mini_deerflow.config.model_config import ModelConfig
from mini_deerflow.config.tool_config import ToolConfig, ToolGroupConfig


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[4]


def get_default_config_path() -> Path:
    backend_root = _backend_root()
    config_path = backend_root / "config.yaml"
    if config_path.exists():
        return config_path
    return backend_root / "config.example.yaml"


def _load_config_payload(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Config file {path} must contain a mapping at the top level.")
    return data


@dataclass(slots=True)
class AppConfig:
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

        return cls(
            models=models,
            tool_groups=tool_groups,
            tools=tools,
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
```

```python
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
```

```python
from mini_deerflow.models.factory import create_chat_model

__all__ = ["create_chat_model"]
```

```python
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from mini_deerflow.config import load_app_config
from mini_deerflow.reflection import resolve_object


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
    """Create a chat model instance from the configured model list."""

    app_config = load_app_config(config_path)
    selected = app_config.models[0] if name is None else app_config.get_model_config(name)
    if selected is None:
        raise ValueError(f"Model {name!r} not found in config {Path(app_config.source_path)}")

    model_class = resolve_object(selected.use)
    init_kwargs = _resolve_env_placeholders(selected.build_init_kwargs())
    init_kwargs.update(overrides)
    return model_class(**init_kwargs)
```

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from langchain_core.messages import AIMessage


def _message_type(message: Any) -> str:
    if hasattr(message, "type"):
        return str(getattr(message, "type"))
    if isinstance(message, dict):
        return str(message.get("role", ""))
    return ""


def _message_content(message: Any) -> str:
    if hasattr(message, "content"):
        return str(getattr(message, "content"))
    if isinstance(message, dict):
        return str(message.get("content", ""))
    return str(message)


@dataclass(slots=True)
class ToolCallingChatModel:
    """Deterministic local model used by P02 tests."""

    model: str
    final_prefix: str = "P02 final answer"
    search_query: str = "P02"
    timezone: str = "UTC"
    bound_tool_names: list[str] = field(default_factory=list)

    def bind_tools(self, tools: list[Any]) -> "ToolCallingChatModel":
        return ToolCallingChatModel(
            model=self.model,
            final_prefix=self.final_prefix,
            search_query=self.search_query,
            timezone=self.timezone,
            bound_tool_names=[getattr(tool, "name", "") for tool in tools],
        )

    def invoke(self, messages: Sequence[Any]) -> AIMessage:
        tool_messages = [message for message in messages if _message_type(message) == "tool"]
        if tool_messages:
            summary = "; ".join(
                f"{getattr(message, 'name', 'tool')}={_message_content(message)}"
                for message in tool_messages
            )
            return AIMessage(content=f"{self.final_prefix}: {summary}")

        tool_calls: list[dict[str, Any]] = []
        if "current_time" in self.bound_tool_names:
            tool_calls.append(
                {
                    "id": "call_current_time",
                    "name": "current_time",
                    "args": {"timezone": self.timezone},
                    "type": "tool_call",
                }
            )
        if "search_stub" in self.bound_tool_names:
            tool_calls.append(
                {
                    "id": "call_search_stub",
                    "name": "search_stub",
                    "args": {"query": self.search_query},
                    "type": "tool_call",
                }
            )
        if not tool_calls and "echo" in self.bound_tool_names:
            tool_calls.append(
                {
                    "id": "call_echo",
                    "name": "echo",
                    "args": {"text": "P02 echo fallback"},
                    "type": "tool_call",
                }
            )

        if not tool_calls:
            return AIMessage(content=f"{self.final_prefix}: no tools requested")

        return AIMessage(content="", tool_calls=tool_calls)
```

```yaml
models:
  - name: fake-tool-model
    display_name: Fake Tool Model
    use: mini_deerflow.models.testing:ToolCallingChatModel
    model: tool-calling

tool_groups:
  - name: builtin
  - name: web

tools:
  - name: search_stub
    group: web
    use: mini_deerflow.community.stub_search.tools:search_stub_tool
    results:
      - Mini DeerFlow P02 search result
```

```yaml
models:
  - name: fake-tool-model
    display_name: Fake Tool Model
    use: mini_deerflow.models.testing:ToolCallingChatModel
    model: tool-calling

tool_groups:
  - name: builtin

tools:
  - name: search_stub
    group: web
    use: mini_deerflow.community.stub_search.tools:search_stub_tool
```

```yaml
models:
  - name: fake-tool-model
    display_name: Fake Tool Model
    use: mini_deerflow.models.testing:ToolCallingChatModel
    model: tool-calling

tool_groups:
  - name: builtin
  - name: web

tools:
  - name: search_stub
    group: web
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/p02_tool_dispatch/test_tool_config.py tests/p02_tool_dispatch/test_example_config.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add P02-tool-dispatch/backend/packages/harness/mini_deerflow tests/fixtures tests/p02_tool_dispatch/test_tool_config.py tests/p02_tool_dispatch/test_example_config.py
git commit -m "feat: add P02 config and model factory foundations"
```

### Task 3: Add builtin tools, configured tool loading, and the unified registry

**Files:**
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/community/__init__.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/community/stub_search/__init__.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/community/stub_search/tools.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/tools/__init__.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/tools/tools.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/tools/builtins/__init__.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/tools/builtins/current_time.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/tools/builtins/echo.py`
- Create: `tests/p02_tool_dispatch/test_tool_registry.py`

- [ ] **Step 1: Write the failing test**

```python
from __future__ import annotations

import unittest

from tests.p02_tool_dispatch.support import REPO_ROOT, ensure_p02_harness_on_path

ensure_p02_harness_on_path()

from mini_deerflow.tools import get_available_tools  # type: ignore  # noqa: E402


class TestP02ToolRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.config_path = REPO_ROOT / "tests" / "fixtures" / "p02-config.yaml"

    def test_get_available_tools_returns_builtin_and_configured_tools(self) -> None:
        tools = get_available_tools(config_path=self.config_path)
        self.assertEqual([tool.name for tool in tools], ["current_time", "echo", "search_stub"])

    def test_get_available_tools_filters_by_requested_group(self) -> None:
        tools = get_available_tools(config_path=self.config_path, groups=["web"])
        self.assertEqual([tool.name for tool in tools], ["search_stub"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/p02_tool_dispatch/test_tool_registry.py -v`
Expected: FAIL because the builtin tools, configured tool factory, and `get_available_tools()` do not exist yet

- [ ] **Step 3: Write minimal implementation**

Implement the builtin tools, configured tool factory, and unified registry:

```python
"""Community tool providers for mini-deerflow P02."""
```

```python
from mini_deerflow.community.stub_search.tools import search_stub_tool

__all__ = ["search_stub_tool"]
```

```python
from __future__ import annotations

from typing import Sequence

from langchain_core.tools import StructuredTool


def search_stub_tool(name: str = "search_stub", results: Sequence[str] | None = None) -> StructuredTool:
    """Create a deterministic configured search stub tool."""

    resolved_results = list(results or ["Mini DeerFlow P02 search result"])

    def _search_stub(query: str) -> str:
        joined_results = " | ".join(resolved_results)
        return f"query={query}; results={joined_results}"

    return StructuredTool.from_function(
        func=_search_stub,
        name=name,
        description="Return deterministic stub search results for testing tool dispatch.",
    )
```

```python
from mini_deerflow.tools.tools import get_available_tools

__all__ = ["get_available_tools"]
```

```python
from __future__ import annotations

from mini_deerflow.tools.builtins.current_time import current_time_tool
from mini_deerflow.tools.builtins.echo import echo_tool


def get_builtin_tools() -> list[tuple[str, object]]:
    return [
        ("builtin", current_time_tool),
        ("builtin", echo_tool),
    ]


__all__ = ["get_builtin_tools", "current_time_tool", "echo_tool"]
```

```python
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langchain_core.tools import StructuredTool


def _current_time(timezone: str = "UTC") -> str:
    try:
        current_time = datetime.now(ZoneInfo(timezone))
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown timezone: {timezone}") from exc
    return f"timezone={timezone}; iso_time={current_time.isoformat()}"


current_time_tool = StructuredTool.from_function(
    func=_current_time,
    name="current_time",
    description="Return the current time in ISO format for a named timezone.",
)
```

```python
from __future__ import annotations

from langchain_core.tools import StructuredTool


def _echo(text: str) -> str:
    return text


echo_tool = StructuredTool.from_function(
    func=_echo,
    name="echo",
    description="Return the provided text unchanged.",
)
```

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/p02_tool_dispatch/test_tool_registry.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add P02-tool-dispatch/backend/packages/harness/mini_deerflow/community P02-tool-dispatch/backend/packages/harness/mini_deerflow/tools tests/p02_tool_dispatch/test_tool_registry.py
git commit -m "feat: add P02 tool registry and builtin tools"
```

### Task 4: Upgrade the lead agent into a minimal tool dispatch graph

**Files:**
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/agents/__init__.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/agents/lead_agent/__init__.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/agents/lead_agent/prompt.py`
- Create: `P02-tool-dispatch/backend/packages/harness/mini_deerflow/agents/lead_agent/agent.py`
- Create: `tests/p02_tool_dispatch/test_lead_agent.py`

- [ ] **Step 1: Write the failing test**

```python
from __future__ import annotations

import unittest

from langgraph.graph.state import CompiledStateGraph

from tests.p02_tool_dispatch.support import REPO_ROOT, ensure_p02_harness_on_path

ensure_p02_harness_on_path()

from mini_deerflow.agents import make_lead_agent  # type: ignore  # noqa: E402


class TestP02LeadAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.config_path = REPO_ROOT / "tests" / "fixtures" / "p02-config.yaml"

    def test_make_lead_agent_runs_model_tools_model_loop(self) -> None:
        agent = make_lead_agent(
            config={"configurable": {"config_path": str(self.config_path)}}
        )

        self.assertIsInstance(agent, CompiledStateGraph)
        result = agent.invoke({"messages": [{"role": "user", "content": "what time is it and search P02"}]})

        self.assertEqual(result["messages"][-1].type, "ai")
        self.assertIn("P02 final answer", result["messages"][-1].content)
        self.assertIn("search_stub=query=P02; results=Mini DeerFlow P02 search result", result["messages"][-1].content)

        tool_messages = [message for message in result["messages"] if getattr(message, "type", "") == "tool"]
        self.assertEqual([message.name for message in tool_messages], ["current_time", "search_stub"])

    def test_make_lead_agent_respects_runtime_tool_groups(self) -> None:
        agent = make_lead_agent(
            config={
                "configurable": {
                    "config_path": str(self.config_path),
                    "tool_groups": ["web"],
                }
            }
        )

        result = agent.invoke({"messages": [{"role": "user", "content": "search P02"}]})
        tool_messages = [message for message in result["messages"] if getattr(message, "type", "") == "tool"]

        self.assertEqual([message.name for message in tool_messages], ["search_stub"])
        self.assertNotIn("current_time=", result["messages"][-1].content)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/p02_tool_dispatch/test_lead_agent.py -v`
Expected: FAIL because the P02 lead agent and prompt modules do not exist yet

- [ ] **Step 3: Write minimal implementation**

Implement the tool-aware prompt and the two-node LangGraph loop:

```python
from mini_deerflow.agents.lead_agent.agent import make_lead_agent

__all__ = ["make_lead_agent"]
```

```python
from mini_deerflow.agents.lead_agent.agent import make_lead_agent

__all__ = ["make_lead_agent"]
```

```python
"""Prompt helpers for the minimal P02 lead agent."""


SYSTEM_PROMPT = """You are mini-deerflow P02, a minimal open-source super agent with tool dispatch.

In this phase you may:
- choose one or more tools when they help answer the user
- read tool results carefully
- produce a direct final answer grounded in those results

Do not assume memory, sandbox, file writing, or subagents exist in this phase.
"""


def get_system_prompt() -> str:
    """Return the minimal system prompt for P02."""
    return SYSTEM_PROMPT
```

```python
from __future__ import annotations

from typing import Any

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from mini_deerflow.agents.lead_agent.prompt import get_system_prompt
from mini_deerflow.models.factory import create_chat_model
from mini_deerflow.tools import get_available_tools


def _extract_runtime_options(config: Any) -> dict[str, Any]:
    if not isinstance(config, dict):
        return {}
    configurable = config.get("configurable")
    if not isinstance(configurable, dict):
        return {}
    return configurable


def _select_next_node(state: MessagesState) -> str:
    messages = state.get("messages", [])
    if not messages:
        return END

    last_message = messages[-1]
    tool_calls = getattr(last_message, "tool_calls", None)
    if isinstance(tool_calls, list) and tool_calls:
        return "run_tools"
    return END


def make_lead_agent(config: dict[str, Any] | None = None) -> Any:
    """Build the minimal lead agent for P02."""

    runtime_options = _extract_runtime_options(config)
    model_name = runtime_options.get("model_name")
    config_path = runtime_options.get("config_path")
    tool_groups = runtime_options.get("tool_groups")

    model = create_chat_model(name=model_name, config_path=config_path)
    tools = get_available_tools(config_path=config_path, groups=tool_groups)
    bound_model = model.bind_tools(tools)
    tool_node = ToolNode(tools)
    system_prompt = get_system_prompt()

    def call_model(state: MessagesState) -> dict[str, list[Any]]:
        messages = state.get("messages", [])
        response = bound_model.invoke([SystemMessage(content=system_prompt), *messages])
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("call_model", call_model)
    graph.add_node("run_tools", tool_node)
    graph.add_edge(START, "call_model")
    graph.add_conditional_edges(
        "call_model",
        _select_next_node,
        {
            "run_tools": "run_tools",
            END: END,
        },
    )
    graph.add_edge("run_tools", "call_model")
    return graph.compile()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/p02_tool_dispatch/test_lead_agent.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add P02-tool-dispatch/backend/packages/harness/mini_deerflow/agents tests/p02_tool_dispatch/test_lead_agent.py
git commit -m "feat: add P02 lead agent tool dispatch loop"
```

### Task 5: Finish the P02 README and run full stage verification

**Files:**
- Modify: `P02-tool-dispatch/README.md`
- Create: `tests/p02_tool_dispatch/test_readme.py`

- [ ] **Step 1: Write the failing test**

```python
from __future__ import annotations

import unittest

from tests.p02_tool_dispatch.support import P02_ROOT


class TestP02Readme(unittest.TestCase):
    def test_readme_mentions_tool_registry_yaml_and_non_goals(self) -> None:
        readme = (P02_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("get_available_tools()", readme)
        self.assertIn("langgraph dev", readme)
        self.assertIn("YAML", readme)
        self.assertIn("sandbox", readme)
        self.assertIn("MCP", readme)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/p02_tool_dispatch/test_readme.py -v`
Expected: FAIL because the current README is only a scaffold and does not explain the finished P02 stage

- [ ] **Step 3: Write minimal implementation**

Expand the stage README so a reader can run the stage and understand its scope:

```markdown
# P02 Tool Dispatch

`P02-tool-dispatch` 是 `mini-deerflow` 的第二阶段代码实现。

它保留了 `P01-the-loop` 的最小主入口形状：

- `backend/langgraph.json`
- `make_lead_agent()`
- `create_chat_model()`

同时新增这一阶段最重要的系统边界：

- `get_available_tools()`
- `tool_groups` 与 `tools` 配置
- builtin tools
- configured tools
- `model -> tools -> model` 的最小闭环

## What You Will Learn

1. 为什么 tool system 应该从主 loop 中独立出来
2. `tool_groups`、`tools`、builtin tools、configured tools 的最小分层
3. 如何用 LangGraph 把一次普通 completion 升级成 `tool_call -> tool_result -> final_answer`
4. 为什么 `P02` 先不接 sandbox、file write、MCP

## Directory Layout

```text
P02-tool-dispatch/
├── README.md
└── backend/
    ├── config.example.yaml
    ├── langgraph.json
    ├── pyproject.toml
    └── packages/harness/mini_deerflow/
        ├── agents/
        ├── community/
        ├── config/
        ├── models/
        ├── reflection/
        └── tools/
```

## Quick Start

```bash
cd P02-tool-dispatch/backend
cp config.example.yaml config.yaml
uv sync
uv run langgraph dev
```

`config.yaml` 与 `config.example.yaml` 在这一阶段使用真实 YAML 写法，而不是 JSON-shaped YAML。

`langgraph.json` 会把 `lead_agent` 指向 `mini_deerflow.agents:make_lead_agent`。运行时 `make_lead_agent()` 会创建一个最小图：

```text
START -> call_model -> run_tools -> call_model -> END
```

## Tool Loading

这一阶段统一通过 `get_available_tools()` 装配工具。

- builtin tools 由 `mini_deerflow.tools.builtins` 提供
- configured tools 由 `config.yaml` 中的 `tools` 配置决定
- `tool_groups` 负责声明允许出现的工具分组

默认 demo 工具包括：

- `current_time`
- `echo`
- `search_stub`

## Config Example

```yaml
models:
  - name: deepseek-v3
    display_name: DeepSeek V3 (Thinking)
    use: langchain_openai:ChatOpenAI
    model: deepseek-reasoner
    base_url: https://api.deepseek.com
    api_key: $DEEPSEEK_API_KEY

tool_groups:
  - name: builtin
  - name: web

tools:
  - name: search_stub
    group: web
    use: mini_deerflow.community.stub_search.tools:search_stub_tool
    results:
      - Mini DeerFlow P02 search result
```

## Non-Goals

这一阶段明确不做：

- sandbox
- file write
- bash execution
- MCP
- memory
- middleware chain
- subagents

## Verification

```bash
python3 -m pytest tests/p02_tool_dispatch -v
python3 -m compileall P02-tool-dispatch/backend
```
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/p02_tool_dispatch/test_readme.py -v`
Expected: PASS

- [ ] **Step 5: Run full stage verification**

Run: `python3 -m pytest tests/p02_tool_dispatch -v`
Expected: all P02 tests pass

- [ ] **Step 6: Run syntax verification**

Run: `python3 -m compileall P02-tool-dispatch/backend`
Expected: exit 0 with no syntax errors

- [ ] **Step 7: Commit**

```bash
git add P02-tool-dispatch/README.md tests/p02_tool_dispatch/test_readme.py
git commit -m "docs: finish P02 tool dispatch documentation"
```
