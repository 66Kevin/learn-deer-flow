# P01 The Loop

`P01-the-loop` 是 `mini-deerflow` 的第一阶段代码实现。它只保留 DeerFlow 2.0 最小、最关键的 4 个元素：

- `backend/langgraph.json`
- `make_lead_agent()`
- `create_chat_model()`
- 一个最小 system prompt

运行时实现上，`make_lead_agent()` 会返回一个单节点 `CompiledStateGraph`：读取消息、调用模型、返回回复。

这一阶段不实现 tools、thread workspace、middleware、sandbox、memory、Gateway 或 Frontend。

## Directory Layout

```text
P01-the-loop/
├── README.md
└── backend/
    ├── .env.example
    ├── config.example.yaml
    ├── langgraph.json
    ├── pyproject.toml
    └── packages/harness/deerflow/
        ├── agents/
        ├── config/
        ├── models/
        └── reflection/
```

## Quick Start

1. 进入 backend 目录
2. 复制环境变量模板并填写 `DEEPSEEK_API_KEY`
3. 复制模型配置文件
4. 安装依赖
5. 启动 `langgraph dev`

```bash
cd P01-the-loop/backend
cp .env.example .env
cp config.example.yaml config.yaml
uv sync
uv run langgraph dev
```

这里的 `uv sync` 会把 `langgraph` Python 包和 `langgraph dev` 所需的 `langgraph` CLI 一起装进当前环境。

`langgraph.json` 会把 `lead_agent` 指向 `deerflow.agents:make_lead_agent`，并默认从 `.env` 加载环境变量。当前 `make_lead_agent()` 会直接构造一个最小 `StateGraph` 并返回 `CompiledStateGraph`，这样可以被 `langgraph dev` 直接注册和运行。

## Config

`config.yaml` 至少需要一个 model：

```yaml
{
  "models": [
    {
      "name": "deepseek-v3",
      "display_name": "DeepSeek V3 (Thinking)",
      "use": "langchain_openai:ChatOpenAI",
      "model": "deepseek-reasoner",
      "base_url": "https://api.deepseek.com",
      "api_key": "$DEEPSEEK_API_KEY"
    }
  ]
}
```

示例中的 `api_key` 会通过环境变量占位符解析，所以需要先在 `.env` 中提供 `DEEPSEEK_API_KEY`。这里默认用 `langchain_openai:ChatOpenAI` 直连 DeepSeek 的 OpenAI-compatible API，并通过 `base_url` 指向 `https://api.deepseek.com`。

为了让本阶段测试不依赖真实外部 API，测试用例使用了本地 `FixedResponseChatModel`。

## VS Code Debug

仓库内置了 [`launch.json`](/Users/wangyueyi/VscodeProjects/learn-deer-flow/.vscode/launch.json) 的 `Attach to LangGraph` 配置，可直接附加到 `langgraph dev` 进程。

先在终端启动带调试端口的 LangGraph Server：

```bash
cd P01-the-loop/backend
uv run langgraph dev --no-browser --port 8000 --debug-port 5678 --wait-for-client
```

执行一次 `uv sync` 后，`debugpy` 会随项目默认依赖一起安装，因此上面的调试命令可以直接使用。

然后在 VS Code 的 Run and Debug 面板选择 `Attach to LangGraph` 并启动。连上后再运行 [`tests/p01_the_loop/test_all.py`](/Users/wangyueyi/VscodeProjects/learn-deer-flow/tests/p01_the_loop/test_all.py) 或发送 HTTP 请求，即可命中断点查看 `config.yaml -> make_lead_agent() -> create_chat_model()` 的调用链。
