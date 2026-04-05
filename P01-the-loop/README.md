# P01 The Loop

`P01-the-loop` 是 `mini-deerflow` 的第一阶段代码实现。它只保留 DeerFlow 2.0 最小、最关键的 4 个元素：

- `backend/langgraph.json`
- `make_lead_agent()`
- `create_chat_model()`
- 一个最小 system prompt

这一阶段故意不实现 tools、thread workspace、middleware、sandbox、memory、Gateway 或 Frontend。

## Directory Layout

```text
P01-the-loop/
  README.md
  backend/
    config.example.yaml
    langgraph.json
    pyproject.toml
    packages/harness/deerflow/
      agents/
      config/
      models/
      reflection/
```

## Quick Start

1. 进入 backend 目录。
2. 复制配置文件。
3. 安装依赖。
4. 启动 `langgraph dev`。

```bash
cd P01-the-loop/backend
cp config.example.yaml config.yaml
uv sync
uv run langgraph dev
```

`langgraph.json` 会把 `lead_agent` 指向 `deerflow.agents:make_lead_agent`。

## Config

`config.yaml` 至少需要一个 model：

```yaml
{
  "models": [
    {
      "name": "default-openai",
      "display_name": "Default OpenAI",
      "use": "langchain_openai:ChatOpenAI",
      "model": "gpt-4.1-mini",
      "api_key": "$OPENAI_API_KEY"
    }
  ]
}
```

为了让本阶段测试不依赖真实外部 API，测试用例使用了本地 `FixedResponseChatModel`。

## What To Read

- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`
- `backend/packages/harness/deerflow/agents/lead_agent/prompt.py`
- `backend/packages/harness/deerflow/models/factory.py`
- `backend/packages/harness/deerflow/config/app_config.py`

如果你能完整看懂这 4 个文件，说明你已经抓住了 `P01` 的重点：`lead_agent` 入口很薄，复杂性还没有回流进 loop。

