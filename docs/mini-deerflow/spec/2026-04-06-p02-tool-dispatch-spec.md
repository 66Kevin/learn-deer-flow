# P02 Tool Dispatch Spec

## Document Status

- Phase: `P02`
- Status: Draft for review
- Date: `2026-04-06`

## Why P02 Exists

`P01-the-loop` 证明了一个最小 agent runtime 可以只有一张 graph、一个 model factory、一次 completion 路径。

但只做到这里，读者还看不见 DeerFlow 2.0 最关键的一层变化来源：agent 并不是靠不断把逻辑塞回 `lead_agent` 变强，而是靠把 action surface 抽到 loop 外面，交给 tools、config 和 runtime boundary 管理。

`P02-tool-dispatch` 的目标，就是在尽量不重写 `P01 loop` 的前提下，引入最小但真实的 tool dispatch system，让 agent 可以：

- 从模型回复中识别 tool call
- 调用已注册的 tools
- 把 tool result 回灌到消息流
- 再次调用模型生成最终答案

## Goals

- 保持 `P01` 的主入口形状不变：`langgraph.json -> make_lead_agent() -> create_chat_model()`
- 新增统一工具装配口 `get_available_tools()`
- 支持 `builtin tools` 与 `configured tools` 共存
- 使用真实 YAML 作为 `config.yaml` / `config.example.yaml` / fixture 的配置格式
- 让 `lead_agent` 从“单次 completion”升级为“model -> tools -> model”的最小闭环
- 保持教学可读性：让读者可以在几十分钟内看懂 P02 的所有关键文件

## Non-Goals

本阶段明确不做下面这些内容：

- 不引入 sandbox provider
- 不接真实文件写入或命令执行
- 不接 MCP
- 不做 memory、thread workspace、middleware chain
- 不做 tool 权限治理
- 不做 deferred tool loading / tool search
- 不做完整 DeerFlow 2.0 的 agent factory、title、todo、subagent 等运行时能力

## Key Design Principles

### 1. The Loop Stays Small

`lead_agent` 只负责组装 graph、绑定 model 和 tools、定义 dispatch flow。

tools 的定义、装配、配置读取不应该回流进 `lead_agent/agent.py`。

### 2. One New System Lever

相对 `P01`，`P02` 只新增一个主要系统概念：tool dispatch。

如果一个需求会把 sandbox、memory、middleware 或 thread state 提前带进来，它就应该被延后到后续阶段。

### 3. YAML Is the Source Format

`P02` 的配置文件和示例必须使用真实 YAML 写法，而不是 JSON-shaped YAML。这样可以与 DeerFlow 2.0 的配置阅读体验保持一致，也能为 `tool_groups` 与 `tools` 的层级表达留出空间。

### 4. Teach Boundaries, Not Just Features

P02 的重点不是“终于可以调工具”，而是“为什么 tools 必须是一层系统，而不是几段 if/else”。

## Reference Modules From DeerFlow 2.0

P02 主要参考 DeerFlow 2.0 的以下模块形状：

- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`
- `backend/packages/harness/deerflow/tools/tools.py`
- `backend/packages/harness/deerflow/tools/builtins/*`
- `backend/packages/harness/deerflow/config/tool_config.py`
- `config.example.yaml`

学习版不会在 P02 阶段复刻完整实现，但要保留这几层边界：

- `lead_agent` 只消费工具列表，不直接内联工具实现
- `tool_config` 负责描述配置模型
- `tools/tools.py` 负责统一装配
- `builtins/` 与 `community/` 体现两类工具来源

## Stage Layout

`P02-tool-dispatch/` 作为与 `P01-the-loop/` 并列的独立阶段目录存在，避免阶段之间互相污染：

```text
P02-tool-dispatch/
├── README.md
└── backend/
    ├── config.example.yaml
    ├── langgraph.json
    ├── pyproject.toml
    └── packages/harness/mini_deerflow/
        ├── agents/
        │   └── lead_agent/
        │       ├── __init__.py
        │       ├── agent.py
        │       └── prompt.py
        ├── community/
        │   └── stub_search/
        │       ├── __init__.py
        │       └── tools.py
        ├── config/
        │   ├── __init__.py
        │   ├── app_config.py
        │   ├── model_config.py
        │   └── tool_config.py
        ├── models/
        │   ├── __init__.py
        │   ├── factory.py
        │   └── testing.py
        ├── reflection/
        │   └── __init__.py
        └── tools/
            ├── __init__.py
            ├── tools.py
            └── builtins/
                ├── __init__.py
                ├── current_time.py
                └── echo.py
```

## Runtime Architecture

P02 的 graph 只从 `P01` 的单节点结构扩展成一个最小闭环：

```text
START
  |
  v
call_model
  |
  +-- no tool_calls --> END
  |
  +-- has tool_calls --> run_tools
                           |
                           v
                        call_model
```

推荐实现方式：

- `call_model` 节点负责：
  - 读取 state 中的消息
  - 调用在 `make_lead_agent()` 构图阶段就已经创建好的 `bound_model`
  - 生成一条新的 assistant message
- `run_tools` 节点负责：
  - 执行最后一条 assistant message 中的 `tool_calls`
  - 生成对应的 tool messages
  - 把 tool result 追加回消息流
- 条件路由函数负责：
  - 检查最后一条 assistant message 是否包含 `tool_calls`
  - 决定进入 `run_tools` 还是结束

推荐优先使用 `langgraph` 的现成 tool node 能力，而不是在 `lead_agent` 中手写大段 dispatch 逻辑。原因不是“偷懒”，而是为了把 P02 的注意力放在系统边界，而不是放在重复实现框架通用能力上。

## Tool System Design

### Unified Entry

`mini_deerflow.tools:get_available_tools()` 是 P02 的核心边界。

建议函数签名：

```python
def get_available_tools(
    config_path: str | os.PathLike[str] | None = None,
    groups: list[str] | None = None,
) -> list[Any]:
    ...
```

职责限定为：

- 读取工具相关配置
- 收集 builtin tools
- 收集 configured/community tools
- 按 group 过滤
- 返回统一的 tool object 列表

它不负责：

- 控制具体 dispatch loop
- 决定什么时候调用工具
- 做 sandbox 或权限判断

### Group Semantics

`tool_groups` 在 P02 中是一个显式 allowlist。

建议约定如下：

- builtin tools 在代码中带有固定 group，例如 `builtin`
- configured tools 必须在配置中声明自己的 `group`
- `get_available_tools()` 先按配置中的 `tool_groups` 过滤，再按运行时传入的 `groups` 做二次过滤

这样可以让 P02 先把“分组”作为系统边界立住，而不提前引入更复杂的权限模型。

### Tool Sources

P02 只保留两类工具来源：

1. `builtin tools`
   直接由 `mini_deerflow.tools.builtins.*` 提供
2. `configured tools`
   通过配置中的 `use` 路径动态加载，演示“外部 provider 接入”

### Minimum Tool Set

P02 的最小工具集建议固定为 3 个：

- `current_time`
  - builtin
  - 纯函数
  - 适合做最直观的 tool-call 演示
- `echo`
  - builtin
  - 纯函数
  - 适合做最小通路测试
- `search_stub`
  - configured/community tool
  - 返回固定结构化结果
  - 用来证明配置驱动的外部工具接入已经成立

这里明确不引入 `bash`、`read_file`、`write_file` 等工具，因为那会提前把 sandbox boundary 混进 P02。

## Configuration Design

P02 在 `models` 之外新增 `tool_groups` 和 `tools`。

推荐 `config.example.yaml` 形状如下：

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

### Config Models

P02 新增两个最小配置模型：

- `ToolGroupConfig`
  - `name`
- `ToolConfig`
  - `name`
  - `group`
  - `use`
  - 以及其他 provider-specific settings

设计要求：

- `ToolConfig` 的额外字段应保存在通用 `settings` 容器中
- 缺少 `name` / `group` / `use` 时必须抛出清晰错误
- `group` 必须能和 `tool_groups` 对应起来；如果引用未知 group，应明确失败而不是静默忽略

## Model Strategy For P02

P02 仍然复用 `P01` 的 `create_chat_model()` 思路，不在本阶段重构 model factory。

为了让测试不依赖真实 provider，本阶段新增一个本地测试模型，例如 `ToolCallingChatModel`。它需要支持两段行为：

- 第一次收到用户问题时，返回带有 `tool_calls` 的 assistant message
- 第二次收到 tool messages 后，返回最终答案

这个测试模型的作用不是模拟通用大模型，而是稳定地证明：

- tool calls 能被图结构识别
- tools 能被调用
- tool result 能被回灌
- 模型能基于 tool result 生成最终回复

## Lead Agent Changes

`make_lead_agent()` 在 P02 中仍然保持“小而薄”，但新增下面几项职责：

- 解析运行时 `config_path` 与可选 `tool_groups`
- 创建 model
- 获取 `get_available_tools()` 返回的工具列表，并生成 `bound_model`
- 构建 `call_model -> run_tools -> call_model` 的最小 graph

它不应该承担下面这些职责：

- 具体工具实现
- 配置 schema 细节
- provider import 细节
- sandbox 判断

## Testing Strategy

P02 的测试仍然遵循 `P01` 的风格：用少量、清晰、边界明确的测试证明系统成立。

最低需要覆盖下面 5 类测试：

### 1. Stage Layout Test

验证 `P02-tool-dispatch/` 作为独立阶段目录存在，且包含最小 backend 入口文件。

### 2. Tool Config Test

验证：

- `tool_groups` 能正确读取
- `tools` 能正确读取
- 缺关键字段时报清晰错误
- tool 引用未知 group 时明确失败

### 3. Tool Registry Test

验证 `get_available_tools()`：

- 同时返回 builtin tools 和 configured tools
- 支持按 group 过滤
- 工具加载失败时给出清晰错误路径

### 4. Lead Agent Dispatch Test

验证一条完整闭环：

1. 用户发起请求
2. 假模型返回两个 tool calls，例如 `current_time` 与 `search_stub`
3. tools 节点执行工具
4. tool result 回灌进消息流
5. 模型返回最终总结文本

### 5. README Test

验证 `P02-tool-dispatch/README.md` 至少说明：

- `get_available_tools()` 的作用
- builtin/configured tools 的区别
- P02 明确不做 sandbox / file write / MCP
- `config.yaml` 使用 YAML 格式

## Demo Expectations

P02 最少要有一个可展示 demo：

- prompt 触发两个不同工具
- trace 中能看到 `assistant(tool_calls) -> tool messages -> final answer`
- 与 `P01` 对比时，能够清楚说明“loop 变复杂了一点，但边界更清楚了”

## Done Criteria

满足下面条件时，P02 才算完成：

- `langgraph dev` 能启动 `P02` 阶段服务
- 默认 YAML 配置可以成功加载 model 和 tools
- 至少一条测试 prompt 能走通 `tool call -> tool result -> final answer`
- 新增/删除工具不要求修改主 loop
- builtin tool 与 configured tool 可以共存
- 配置错误有清晰失败路径
- `make_lead_agent()` 仍然足够小，读者可以较快读完整体实现

## Transition To P03

完成 P02 后，系统已经第一次拥有了 action surface，但它仍然缺少“每次运行的稳定工作上下文”。

因此下一阶段 `P03-thread-state` 的自然问题是：

“当 agent 开始真正调工具以后，消息之外的 thread data、workspace、路径信息应该放在哪里？”
