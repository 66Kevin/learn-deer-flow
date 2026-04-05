# P01 The Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an isolated `P01-the-loop` stage project that mirrors DeerFlow 2.0's minimal backend entry path with one `lead_agent`, one model factory, and one completion path.

**Architecture:** The stage will live in a root-level `P01-the-loop/` folder and keep DeerFlow 2.0's `backend/langgraph.json` and `packages/harness/deerflow/...` shape. A small YAML-backed model config loader, a reflection helper, and a minimal `make_lead_agent()` factory will be enough for this phase. Tests will use a local fake chat model so the stage is runnable without external API calls.

**Tech Stack:** Python 3.12+, `langchain`, `langgraph`, `pydantic`, `pyyaml`, `pytest`

---

### Task 1: Scaffold the isolated P01 stage project

**Files:**
- Create: `P01-the-loop/README.md`
- Create: `P01-the-loop/backend/pyproject.toml`
- Create: `P01-the-loop/backend/langgraph.json`
- Create: `P01-the-loop/backend/config.example.yaml`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path


def test_stage_layout_has_minimal_backend_entrypoints():
    root = Path("P01-the-loop/backend")
    assert (root / "langgraph.json").exists()
    assert (root / "pyproject.toml").exists()
    assert (root / "config.example.yaml").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/p01_the_loop/test_layout.py -v`
Expected: FAIL because `P01-the-loop/backend` and required files do not exist yet

- [ ] **Step 3: Write minimal implementation**

Create the stage folder and minimal backend metadata files with DeerFlow 2.0-aligned paths:

```toml
[project]
name = "mini-deerflow-p01"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "langchain>=1.2.3",
  "langgraph>=1.0.6,<1.0.10",
  "pydantic>=2.12.5",
  "pyyaml>=6.0.3",
]
```

```json
{
  "$schema": "https://langgra.ph/schema.json",
  "python_version": "3.12",
  "dependencies": ["."],
  "graphs": {
    "lead_agent": "deerflow.agents:make_lead_agent"
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/p01_the_loop/test_layout.py -v`
Expected: PASS

### Task 2: Add config loading and model factory tests first

**Files:**
- Create: `P01-the-loop/backend/packages/harness/deerflow/config/model_config.py`
- Create: `P01-the-loop/backend/packages/harness/deerflow/config/app_config.py`
- Create: `P01-the-loop/backend/packages/harness/deerflow/config/__init__.py`
- Create: `P01-the-loop/backend/packages/harness/deerflow/reflection/__init__.py`
- Create: `tests/p01_the_loop/test_model_factory.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from deerflow.config import load_app_config
from deerflow.models.factory import create_chat_model


def test_load_app_config_reads_first_model_from_yaml():
    config = load_app_config(Path("tests/fixtures/p01-config.yaml"))
    assert config.models[0].name == "fake-default"


def test_create_chat_model_uses_default_model_when_name_missing():
    model = create_chat_model(config_path=Path("tests/fixtures/p01-config.yaml"))
    assert model.__class__.__name__ == "FixedResponseChatModel"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/p01_the_loop/test_model_factory.py -v`
Expected: FAIL because config modules and factory do not exist yet

- [ ] **Step 3: Write minimal implementation**

Implement:
- a `ModelConfig` pydantic model
- an `AppConfig` wrapper with `models` and `get_model_config(name)`
- a YAML loader that reads `config.yaml` or a provided path
- a reflection helper that resolves `module:Class` and `module.Class`
- `create_chat_model()` that uses the first configured model by default

Also add a local fake provider class for tests.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/p01_the_loop/test_model_factory.py -v`
Expected: PASS

### Task 3: Add lead agent assembly and invocation tests first

**Files:**
- Create: `P01-the-loop/backend/packages/harness/deerflow/agents/__init__.py`
- Create: `P01-the-loop/backend/packages/harness/deerflow/agents/lead_agent/__init__.py`
- Create: `P01-the-loop/backend/packages/harness/deerflow/agents/lead_agent/prompt.py`
- Create: `P01-the-loop/backend/packages/harness/deerflow/agents/lead_agent/agent.py`
- Create: `P01-the-loop/backend/packages/harness/deerflow/models/testing.py`
- Create: `tests/p01_the_loop/test_lead_agent.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from deerflow.agents import make_lead_agent


def test_make_lead_agent_returns_runnable_graph():
    agent = make_lead_agent(config={"configurable": {"config_path": "tests/fixtures/p01-config.yaml"}})
    result = agent.invoke({"messages": [{"role": "user", "content": "hello"}]})
    assert result["messages"][-1].content == "P01 says hello"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/p01_the_loop/test_lead_agent.py -v`
Expected: FAIL because lead agent modules do not exist yet

- [ ] **Step 3: Write minimal implementation**

Implement:
- a minimal system prompt helper
- `make_lead_agent()` that creates a model from config and uses `langchain.agents.create_agent`
- a local `FixedResponseChatModel` for tests that always returns a configured response

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/p01_the_loop/test_lead_agent.py -v`
Expected: PASS

### Task 4: Add smoke documentation and verification

**Files:**
- Modify: `P01-the-loop/README.md`
- Create: `tests/fixtures/p01-config.yaml`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path


def test_readme_mentions_langgraph_entry_and_default_run_steps():
    readme = Path("P01-the-loop/README.md").read_text()
    assert "langgraph dev" in readme
    assert "make_lead_agent" in readme
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/p01_the_loop/test_readme.py -v`
Expected: FAIL because README does not contain run instructions yet

- [ ] **Step 3: Write minimal implementation**

Add:
- directory overview
- local dev commands
- sample `config.yaml` copy step
- explanation that this stage intentionally omits tools, sandbox, memory, and frontend

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/p01_the_loop/test_readme.py -v`
Expected: PASS

- [ ] **Step 5: Run full stage verification**

Run: `python3 -m pytest tests/p01_the_loop -v`
Expected: all P01 tests pass

- [ ] **Step 6: Run syntax verification**

Run: `python3 -m compileall P01-the-loop/backend`
Expected: exit 0 with no syntax errors

