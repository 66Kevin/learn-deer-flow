# P02 Tool Dispatch

`P02-tool-dispatch` 是 `mini-deerflow` 的第二阶段代码实现。

这一阶段会在 `P01-the-loop` 的最小 graph 基础上加入最小 tool dispatch loop：

- `get_available_tools()`
- builtin tools
- configured tools
- `model -> tools -> model`
