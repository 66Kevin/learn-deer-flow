# P05 Planning

> complex tasks need explicit decomposition

## 本阶段目标

把 agent 从“会调工具”升级成“会先拆任务再执行”。在 `DeerFlow 2.0` 里，这一层更接近 runtime feature，而不是 `1.x` 那种中心 planner graph。

## 架构范围

本阶段新增：

- `plan mode`
- todo list / task tracking
- 面向复杂任务的 prompt contract
- 在执行过程中持续更新任务状态

这一阶段的重点是“显式分解”，不是“多 agent 协作”。

## 推荐实现目标

- 为复杂任务启用 `plan mode`
- 提供 `write_todos` 或等价能力
- 让 agent 在开始执行前形成一个可见计划
- 在执行过程中更新 `pending/in_progress/completed`
- 简单任务仍然可以直接执行，不强制进入 plan mode

## 推荐落地文件

- `backend/packages/harness/deerflow/agents/middlewares/todo_middleware.py`
- `backend/packages/harness/deerflow/agents/thread_state.py`
- `backend/packages/harness/deerflow/agents/lead_agent/prompt.py`
- `backend/packages/harness/deerflow/config/agents_config.py` 的相关开关

## 为什么这一阶段要放在这里

只有在 `ThreadState` 和 `Middleware` 都建立之后，planning 才适合作为一个运行时能力落地。否则 todo 数据很容易和 loop、tool result、product UI 混成一团。

## 明确不做

- 不做 subagent delegation
- 不做后台任务系统
- 不做团队协作协议
- 不把 planning 实现成另一个庞大 graph

## 完成标准

- 复杂任务能先生成 todo list 再执行
- todo 状态在执行过程中真实变化
- 简单任务不会被 planning 机制拖慢
- todo 数据能进入 state，并可被后续 UI 或 runtime services 消费

## 核心学习点

- planning 不是“多写一个 planner 节点”这么简单，关键在于它怎样进入 runtime
- 一个好的 plan mode 既要帮助复杂任务，也不能伤害简单任务
- todo list 既是执行辅助，也是后续 `subagents`、`frontend`、`runtime services` 的共享结构

## 对应 DeerFlow 2.0 模块

- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`
- `backend/packages/harness/deerflow/agents/middlewares/todo_middleware.py`

## 推荐公开 demo

- 一个复杂 prompt，展示 todo list 从创建到完成
- 一张图：`simple task bypasses plan mode / complex task enters plan mode`
- 一张 UI 草图：后续前端会如何消费 todos

## 进入下一阶段前必须确认

- planning 已经是系统结构的一部分，不是 prompt 小技巧
- todos 已经成为 state 中稳定字段
- 你已经准备好在下一阶段把“任务方法论”升级成“skills 注入”

