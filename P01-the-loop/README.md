# P01 The Loop

`P01-the-loop` 是 `mini-deerflow` 的第一阶段代码实现。它只保留 `mini-deerflow` 最小、最关键的 4 个元素：

- `backend/langgraph.json`
- `make_lead_agent()`
- `create_chat_model()`
- 一个最小 system prompt

运行时实现上，`make_lead_agent()` 会返回一个单节点 `CompiledStateGraph`：读取消息、调用模型、返回回复。

这一阶段不实现 tools、thread workspace、middleware、sandbox、memory、Gateway 或 Frontend。

## What You Will Learn

在这一阶段中，你可以重点学到下面这些内容：

1. **如何使用 LangGraph 构建一个最小化的 agent**
   这一章会带你看到，一个最小可运行的 agent 并不需要复杂的多节点编排。只要有一个清晰的 graph 入口、一个读取消息并调用模型的节点，以及一个稳定的状态结构，就已经可以形成最基础的 agent runtime。
2. **为什么在 mini-deerflow 中要使用反射式的动态模型创建机制**
   这一章会展示为什么 `create_chat_model()` 不是直接在代码里写死 `ChatOpenAI(...)`，而是通过配置中的 `use` 字段配合动态反射来创建 LLM。这样做的核心价值是让 agent runtime 和具体 provider 解耦：切换 OpenAI-compatible provider、接入测试假模型、或者替换为后续自定义 patch 类时，都不需要改 `lead_agent` 本身。
3. **这种配置驱动方式相比直接写死模型代码的取舍**
   动态反射的好处是灵活、可扩展、便于测试，也更接近 mini-deerflow 这类 harness 的设计思路；代价则是错误会更多地在运行时暴露，而不是在写代码时由 IDE 或类型系统提前发现。理解这组取舍，是这一章非常重要的学习点。
4. **如何使用 `langgraph.json` 和 `langgraph dev` 来启动 agent 服务**
   你会理解 `langgraph.json` 在 LangGraph 项目中的角色：它负责声明 graph 的注册入口、依赖和环境变量来源；而 `langgraph dev` 则把这个 graph 作为本地服务跑起来，让你能够通过 HTTP 或 SDK 直接向 agent 发消息。
5. **如何在 VS Code 中调试 LangGraph**
   这一章不仅能让你把服务跑起来，还能看到如何把 `langgraph dev` 进程接入 VS Code 调试器。这样你就可以沿着 `config.yaml -> make_lead_agent() -> create_chat_model() -> model.invoke()` 这条链路逐步下断点，真正看清一次请求是怎样流过整个最小 runtime 的。
6. **如何把 agent 入口和模型创建逻辑拆开**
   `lead_agent` 本身只负责组装 graph 和组织消息流，而模型的读取、选择和实例化被放进单独的 model factory 中。这种拆分虽然看起来比全写在一个文件里多了一层，但能明显降低主 loop 被 provider 细节污染的风险。

## Directory Layout

```text
P01-the-loop/
├── README.md
└── backend/
    ├── .env.example
    ├── config.example.yaml
    ├── langgraph.json
    ├── pyproject.toml
    └── packages/harness/mini_deerflow/
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

`langgraph.json` 会把 `lead_agent` 指向 `mini_deerflow.agents:make_lead_agent`，并默认从 `.env` 加载环境变量。当前 `make_lead_agent()` 会直接构造一个最小 `StateGraph` 并返回 `CompiledStateGraph`，这样可以被 `langgraph dev` 直接注册和运行。

## Send a Test Message

当 `uv run langgraph dev` 成功启动后，可以打开另一个终端，使用下面两种方式向 `lead_agent` 发送消息做联调。

### Option 0: Use LangSmith Studio

如果你使用下面这条命令启动服务：

```bash
cd P01-the-loop/backend
uv run langgraph dev --port 8000
```

LangGraph 会启动本地 Agent Server，并自动打开浏览器进入 LangSmith Studio。你可以在 Studio 中：

- 直接向 `lead_agent` 发送消息
- 查看每次 run 的输入与输出
- 观察 graph 的执行过程和消息状态
- 作为最直观的可视化调试入口来联调这个最小 agent

如果浏览器没有自动打开，也可以手动访问：

```text
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8000
```

如果你使用的是 `--no-browser`，则不会自动打开 Studio，需要手动访问上面的地址。

### Option 1: Use `curl`

```bash
curl -N \
  -X POST http://localhost:8000/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "lead_agent",
    "input": {
      "messages": [
        {
          "role": "human",
          "content": "你好，请做个自我介绍"
        }
      ]
    },
    "stream_mode": "values"
  }'
```

这个请求会直接调用 LangGraph 本地服务的 `/runs/stream` 接口。返回内容是流式事件，最后一个 `values` 事件中会包含完整的 `messages` 列表和 assistant 的回复。

### Option 2: Run `test_all.py`

也可以直接运行仓库里的联调脚本：

```bash
P01-the-loop/backend/.venv/bin/python tests/p01_the_loop/test_all.py
```

这个脚本默认连接 `http://localhost:8000`，会：

- 流式打印每个 LangGraph 事件
- 在结束时额外打印 `All LLM replies:`
- 输出本次 run 中收集到的所有 LLM 回复文本

如果你把 `langgraph dev` 启动在别的端口上，需要同步修改 [`tests/p01_the_loop/test_all.py`](/Users/wangyueyi/VscodeProjects/learn-deer-flow/tests/p01_the_loop/test_all.py) 里的 `url`。

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

- **--wait-for-client** 会让服务先停住，等你 IDE 连上后再继续

然后在 VS Code 的 Run and Debug 面板选择 `Attach to LangGraph` 并启动。连上后再运行 [`tests/p01_the_loop/test_all.py`](/Users/wangyueyi/VscodeProjects/learn-deer-flow/tests/p01_the_loop/test_all.py) 或发送 HTTP 请求，即可命中断点查看 `config.yaml -> make_lead_agent() -> create_chat_model()` 的调用链
