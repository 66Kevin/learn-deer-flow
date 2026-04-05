# P03 Thread State

> every run belongs to a workspace

## 本阶段目标

把“单次运行”升级成“属于某个 thread 的运行”。每个 thread 都应该拥有自己的状态与工作目录，否则后面的 `uploads`、`artifacts`、`memory`、`sandbox` 都会缺少稳定锚点。

## 架构范围

本阶段新增：

- `ThreadState`
- `thread_id`
- `thread_data`
- 每线程独立的 `workspace/uploads/outputs`

它解决的是 runtime identity 问题，而不是 UI 层的“会话列表”问题。

## 推荐实现目标

- 定义扩展自 `AgentState` 的 `ThreadState`
- 让每次运行都绑定一个 `thread_id`
- 基于 `thread_id` 生成稳定目录
- 让后续 tools 能通过 state 拿到当前 thread 的工作目录

## 推荐落地文件

- `backend/packages/harness/deerflow/agents/thread_state.py`
- `backend/packages/harness/deerflow/config/paths.py`
- `backend/packages/harness/deerflow/runtime/store/*` 的最小版本
- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`

如果此时还没正式引入 middleware，也可以先把 thread data 初始化写在 factory 中，但要明确它下一阶段会迁移到 middleware。

## 明确不做

- 不做正式 uploads API
- 不做 artifacts 服务
- 不做 memory facts
- 不做持久化 checkpointer

## 完成标准

- 不同 thread 的运行数据严格隔离
- 同一 thread 的工作目录命名规则稳定、可推导
- 后续 phases 可以基于 `ThreadState` 继续扩展，而不用推翻字段设计
- 至少能演示两个 thread 生成不同输出文件且互不干扰

## 核心学习点

- `workspace` 不是产品细节，而是 harness runtime 的基本单位
- `thread state` 必须在 `sandbox` 与 `artifacts` 之前落地，否则边界会漂
- 把 thread identity 设计清楚，后面很多服务层能力都会自然很多

## 对应 DeerFlow 2.0 模块

- `backend/packages/harness/deerflow/agents/thread_state.py`
- `backend/packages/harness/deerflow/config/paths.py`
- `backend/packages/harness/deerflow/agents/middlewares/thread_data_middleware.py`

## 推荐公开 demo

- 两个 thread 各自写入不同 `outputs/` 的截图
- 一张图：`thread_id -> workspace/uploads/outputs`
- 一段说明：为什么“每次运行都有 workspace”是 2.0 和普通聊天 demo 的分水岭

## 进入下一阶段前必须确认

- `ThreadState` 已经成型
- 目录结构已经能稳定派生
- 你已经能解释为什么 thread data 最终应该由 middleware 负责初始化

