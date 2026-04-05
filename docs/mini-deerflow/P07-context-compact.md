# P07 Context Compact

> long sessions need compression

## 本阶段目标

让长会话可以继续活下去，而不是一旦上下文变长就退化。`DeerFlow 2.0` 的思路不是把一切都放进 memory，而是先用 `summarization / compact` 控制会话体积。

## 架构范围

本阶段新增：

- `SummarizationMiddleware`
- trigger / keep 策略
- summary prompt
- 对非消息状态的保护策略

这里处理的是“短中期上下文治理”，不是“长期记忆”。

## 推荐实现目标

- 当消息数或 token 数达到阈值时触发 compact
- 保留最近消息与关键消息
- 用较轻量 model 或同一 model 的轻模式生成摘要
- 确保 `todos`、`thread_data`、`artifacts` 等结构不因 compact 丢失

## 推荐落地文件

- `backend/packages/harness/deerflow/config/summarization_config.py`
- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`
- `backend/packages/harness/deerflow/agents/thread_state.py`
- 可选：单独的 summary prompt 文件

## 明确不做

- 不把 summary 当作长期 memory facts
- 不在本阶段引入复杂 memory retrieval
- 不引入跨 thread 的知识共享

## 完成标准

- 一段人为拉长的对话可以在 compact 后继续执行
- compact 之后 agent 不会丢掉当前工作目标
- 非 message state 不会因 compact 失真
- compact 行为对调用者可观测，而不是黑盒发生

## 核心学习点

- 长会话问题首先是 context budget 问题，其次才是 memory 问题
- compact 不是简单“压缩历史”，而是有选择地保留任务连续性
- middleware 是做 compact 的理想位置，因为它天然位于 model invocation 边界上

## 对应 DeerFlow 2.0 模块

- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`
- `backend/packages/harness/deerflow/config/summarization_config.py`

## 推荐公开 demo

- 一条超长会话的 before/after token 对比
- 一张图：`history -> summarize -> keep recent -> continue`
- 一段解释：为什么 summary 不等于 memory

## 进入下一阶段前必须确认

- 你能明确区分 `context compact` 与 `memory`
- compact 后仍能保持任务连续性
- 你已经准备把真正高风险的执行能力放进 `Sandbox`

