# P02 Tool Dispatch

`P02-tool-dispatch` 是 `mini-deerflow` 的第二阶段代码实现。

当前阶段已经从纯 scaffold 前进到一套最小可测试的后端基础层，用来承接后续的 tool dispatch 闭环。

当前已具备的内容包括：

- YAML-backed `AppConfig` / `ModelConfig` / `ToolConfig`
- `tool_groups` 与 configured tools 的基础校验
- `create_chat_model()` 的最小模型工厂
- 一个用于本地测试的确定性 `ToolCallingChatModel`
- `get_available_tools()` 统一工具注册表
- 内建 builtin tools：`current_time`、`echo`
- 通过配置与反射加载的 configured tool 装配能力
- 一个用于验证 dispatch 配置链路的 `search_stub` community tool provider

这一阶段接下来会继续在这些基础之上补齐：

- `model -> tools -> model` 的最小 dispatch loop
- lead-agent / graph 入口中的 tool dispatch 集成
