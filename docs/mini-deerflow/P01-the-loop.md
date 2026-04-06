# P01 The Loop

> one graph, one model, one completion

## 本阶段目标

实现一个最小可运行的 `lead_agent`：只有一张 graph、一个 model、一次 completion 路径，没有 tools、没有 thread persistence、没有 product shell。

这是整套路线最重要的地基。后面的所有阶段都默认 `loop` 本身尽量稳定，新增复杂性优先放到 loop 外面。

## 架构范围

本阶段只保留 4 个元素：

- `langgraph.json`
- `make_lead_agent()`
- `create_chat_model()`
- 一个最小 system prompt

可以把它理解为 `mini-deerflow` 在 P01 阶段的“裸 harness”。

## 推荐实现目标

- 能通过 `LangGraph Server` 启动一个默认 agent
- 能读取 `config.yaml` 中至少一个 model 配置
- 用户输入一条消息后，agent 可以返回一条普通文本回复
- 运行路径中不依赖 tools、thread workspace、middleware、Gateway、Frontend

## 推荐落地文件

- `backend/langgraph.json`
- `backend/packages/harness/mini_deerflow/agents/lead_agent/agent.py`
- `backend/packages/harness/mini_deerflow/models/factory.py`
- `backend/packages/harness/mini_deerflow/agents/lead_agent/prompt.py`
- `backend/packages/harness/mini_deerflow/config/model_config.py`

## 明确不做

- 不接 tool calling
- 不创建 thread workspace
- 不做 SSE streaming 细节
- 不做 auto title / todos / memory / sandbox
- 不接 `Gateway API` 与 `Frontend`

## 完成标准

- 能成功启动 `langgraph dev`
- 能用默认 model 跑通一次最小对话
- 切换 model 名称不会要求改 agent 代码
- `make_lead_agent()` 仍然足够小，读者可以在几分钟内完整看懂

## 核心学习点

- `DeerFlow 2.0` 的主入口不是一堆 research nodes，而是一个 `lead_agent` factory
- 最小 agent runtime 的核心不是“功能多”，而是“边界清晰”
- model factory 必须独立存在，否则后续的 `thinking`、`vision`、provider patching 很快会污染主 loop

## 对应 DeerFlow 2.0 模块

- `backend/langgraph.json`
- `backend/packages/harness/mini_deerflow/agents/lead_agent/agent.py`
- `backend/packages/harness/mini_deerflow/models/factory.py`

## 推荐公开 demo

- 一张最小架构图：`langgraph.json -> make_lead_agent -> model -> response`
- 一段最小 trace：展示只有一次 completion，没有 tool call
- 一张源码截图：强调 `lead_agent` 入口其实很薄

## 进入下一阶段前必须确认

- 你已经接受“loop 应该尽量小”这个前提
- model factory 和 agent factory 已经分离
- 这个最小版本即使功能弱，也已经是一个真实的 agent runtime
