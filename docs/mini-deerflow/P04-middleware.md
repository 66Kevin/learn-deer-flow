# P04 Middleware

> cross-cutting concerns live outside the loop

## 本阶段目标

把那些“不属于核心 loop、但又几乎每次运行都要经过”的能力迁移到 middleware chain 中。`DeerFlow 2.0` 的一个关键架构选择，就是把大量 runtime complexity 外置到 middleware。

## 架构范围

本阶段至少引入这类 middleware：

- `ThreadDataMiddleware`
- 一个错误处理或结果规范化 middleware
- 一个轻量 metadata middleware，例如 `TitleMiddleware` 的简化版

重点不是数量，而是让顺序、职责和扩展点成型。

## 推荐实现目标

- 定义清晰的 middleware order
- 把 thread data 初始化从 `agent factory` 挪到 middleware
- 把 tool error normalization 从 tool 本身挪到 middleware
- 让 `lead_agent` 只负责组装 middleware，而不直接承担具体逻辑

## 推荐落地文件

- `backend/packages/harness/deerflow/agents/middlewares/thread_data_middleware.py`
- `backend/packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py`
- `backend/packages/harness/deerflow/agents/middlewares/title_middleware.py`
- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`

## 推荐的顺序意识

一开始就应该让读者看到：middleware order 不是“实现细节”，而是架构的一部分。

例如：

1. 先初始化 thread data
2. 再注入和执行 tools 相关上下文
3. 再做 metadata 衍生
4. 最后做需要拦截最终输出的逻辑

## 明确不做

- 不把所有未来 middleware 一次性塞进来
- 不在本阶段讲 `SummarizationMiddleware`
- 不在本阶段讲 `MemoryMiddleware`
- 不在本阶段讲 `SubagentLimitMiddleware`

## 完成标准

- loop 本身相比 `P03` 基本不再增长
- 新增 cross-cutting concern 时，优先改 middleware list 而不是 agent core
- 至少能展示一个“删掉某个 middleware 也不影响其他层”的例子
- middleware 顺序有文档说明，而不是靠读源码猜

## 核心学习点

- 一个成熟 harness 的复杂性，很多时候应该落在 middleware chain，而不是 graph node 数量
- middleware 让功能演进变成“装配问题”，而不是“重写主流程”
- 只有先建立 middleware 心智，后面的 `planning / skills / compact / sandbox` 才会显得自然

## 对应 DeerFlow 2.0 模块

- `backend/packages/harness/deerflow/agents/middlewares/*`
- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`

## 推荐公开 demo

- 一张 middleware execution order 图
- 一段 log trace，标出每个 middleware 的进入点
- 一个 before/after 对比：把 thread init 从 core 挪到 middleware 之后，core 变薄了多少

## 进入下一阶段前必须确认

- 你已经接受 middleware 是 2.0 的主要扩展点
- thread data 与错误处理已经成功迁移出核心 loop
- 你知道后续 phases 为什么优先继续往 middleware 上挂

