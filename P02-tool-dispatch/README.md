# P02 Tool Dispatch

`P02-tool-dispatch` 是 `mini-deerflow` 的第二阶段代码实现。它保留 `P01-the-loop` 的最小入口形状：

- `backend/langgraph.json`
- `make_lead_agent()`
- `create_chat_model()`

在这个基础上，P02 额外把工具装配和调度抽成独立层：

- `get_available_tools()`
- `tool_groups`
- `tools`
- builtin tools live in code under `mini_deerflow.tools.builtins`
- configured tools are loaded from the active config path (`config.yaml` in normal use; `config.example.yaml` is the example starting point)
- 最小的 `model -> tools -> model` loop

## What You Will Learn

1. 为什么工具系统应该从主 loop 中拆出去。
2. `tool_groups`、`tools`、builtin tools、configured tools 的最小分层。
3. 如何把普通 completion 升级成 `tool_call -> tool_result -> final_answer`。
4. 为什么 `P02` 先不接 `sandbox`、`MCP`、memory 或更重的权限边界。

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

`backend/config.example.yaml` is real YAML, not a JSON-shaped example. You can copy it to `config.yaml` and start the stage with `uv run langgraph dev`.

```bash
cd P02-tool-dispatch/backend
cp config.example.yaml config.yaml
uv sync
uv run langgraph dev
```

`langgraph.json` 会把 `lead_agent` 指向 `mini_deerflow.agents:make_lead_agent`。`make_lead_agent()` 读取配置后，会用 `create_chat_model()` 创建模型，再通过 `get_available_tools()` 绑定 builtin tools 和 configured tools，组成最小 dispatch loop。

The shipped `config.example.yaml` uses a DeepSeek-compatible model config, so set `DEEPSEEK_API_KEY` before sending real requests.

## Demo Tools

P02 自带的演示工具包括：

- `current_time`
- `echo`
- `search_stub`

它们的作用是把工具注册、配置加载、反射装配和消息回灌这条链路跑通，而不是提供完整生产能力。

## Non-Goals

这一阶段明确不做：

- `sandbox`
- `MCP`
- 文件读写工具
- 子代理系统
- 复杂权限治理

## Verification

```bash
PYTHONPATH=. uv run --project P02-tool-dispatch/backend --with pytest python -m pytest tests/p02_tool_dispatch -v
python3 -m compileall P02-tool-dispatch/backend
```

如果你只想检查 README 是否仍然对齐当前阶段内容，可以先跑 `tests/p02_tool_dispatch/test_readme.py`。
