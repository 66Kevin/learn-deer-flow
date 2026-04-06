# P02 Tool Dispatch

`P02-tool-dispatch` 是 `mini-deerflow` 的第二阶段代码实现。

当前阶段已经从纯 scaffold 前进到一套最小可测试的后端基础层，用来承接后续的 tool dispatch 闭环。

当前已具备的内容包括：

- YAML-backed `AppConfig` / `ModelConfig` / `ToolConfig`
- `tool_groups` 与 configured tools 的基础校验
- `create_chat_model()` 的最小模型工厂
- 一个用于本地测试的确定性 `ToolCallingChatModel`

这一阶段接下来会继续在这些基础之上补齐：

- `get_available_tools()`
- builtin tools
- configured tools 装配
- `model -> tools -> model` 的最小 dispatch loop
