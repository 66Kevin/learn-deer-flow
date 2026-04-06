# P02 Tool Dispatch

`P02-tool-dispatch` 是 `mini-deerflow` 的第二阶段代码实现。

当前仓库里这一阶段只完成了最小 scaffold，用来为后续的 tool dispatch 实现预留独立的 stage 结构。

这一阶段正在为 `P01-the-loop` 的最小 graph 之上继续扩展做准备，后续会逐步补齐这些能力：

- `get_available_tools()`
- builtin tools
- configured tools
- `model -> tools -> model`

现在这些内容还没有实现，这个目录只负责把 P02 的独立入口、backend 元数据和测试布局先搭起来，方便后续继续迭代。
