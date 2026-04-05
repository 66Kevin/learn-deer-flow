# P02 Tool Dispatch

> the loop stays the same, tools plug in

## 本阶段目标

在不重写 `P01 loop` 的前提下，引入可插拔的 tool system，让 agent 开始拥有 action surface。

这一阶段的重点不是把最强工具一次性接满，而是让读者真正看懂：tool 的复杂性应该落在 registry、config 和 adapter 上，而不是回流进主 loop。

## 架构范围

本阶段新增：

- tool registry
- builtin tools
- configured tools
- community tool adapter 的最小接口

建议先从 2-4 个确定性强、容易解释的工具开始，不要直接跳到完整 sandbox bash。

## 推荐实现目标

- 定义 `get_available_tools()` 作为统一装配入口
- 支持从配置中启用或关闭某些 tools
- 支持 builtin tools 与外部 tool provider 共存
- agent 能根据模型返回结果触发 1 次或多次 tool 调用
- tool result 能正确回灌进消息流

## 推荐落地文件

- `backend/packages/harness/deerflow/tools/tools.py`
- `backend/packages/harness/deerflow/tools/__init__.py`
- `backend/packages/harness/deerflow/tools/builtins/*`
- `backend/packages/harness/deerflow/config/tool_config.py`
- `backend/packages/harness/deerflow/community/<tool-provider>/*`

## 建议的最小工具集

- 一个纯函数类 tool，例如 `current_time` 或 `echo`
- 一个轻量内容获取类 tool，例如 `web_fetch_stub` 或 `search_stub`
- 一个演示型 builtin tool，例如 `present_file` 的极简版本

这里故意不建议在 `P02` 就引入真正的 `bash/read_file/write_file`，因为那会提前把 `sandbox boundary` 混进来。

## 明确不做

- 不在本阶段引入 sandbox provider
- 不做复杂的 tool 权限治理
- 不接 MCP
- 不做 tool search / deferred registry

## 完成标准

- loop 本身与 `P01` 相比几乎不变
- tools 的增删不需要改主 agent loop
- 至少有一条 prompt 能触发多轮 `tool -> tool_result -> final answer`
- tool 配置错误会有清晰失败路径，而不是静默忽略

## 核心学习点

- agent loop 的稳定性来自“把变化放到 tools，而不是放回 loop”
- tool system 至少要分清 `definition`、`configuration`、`loading`
- 真正的扩展性来自统一装配口，而不是 everywhere import tools

## 对应 DeerFlow 2.0 模块

- `backend/packages/harness/deerflow/tools/tools.py`
- `backend/packages/harness/deerflow/tools/builtins/*`
- `backend/packages/harness/deerflow/config/tool_config.py`
- `backend/packages/harness/deerflow/community/*`

## 推荐公开 demo

- 一张图：`model -> get_available_tools() -> tool call -> tool result`
- 一个 prompt：让 agent 调 2 个不同 tool 再总结
- 一张对比图：`P01` 没工具，`P02` 有工具，但 loop 没变

## 进入下一阶段前必须确认

- tool dispatch 已经是系统的一层，而不是几段 if/else
- 你能解释 builtin tool 与 configured tool 的区别
- 你知道为什么真正的文件/命令执行要留到 `P08 Sandbox`

