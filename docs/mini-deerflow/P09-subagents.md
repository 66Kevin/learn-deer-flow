# P09 Subagents

> delegation creates scale

## 本阶段目标

让 `lead_agent` 可以把边界清晰的子任务委派给 subagent，以换取更好的上下文隔离、更清晰的职责边界和有限并发能力。

这一阶段是 DeerFlow 2.0 从“强单 agent”进化到“可扩展 harness”的另一个关键分水岭。

## 架构范围

本阶段新增：

- `task_tool` 或等价委派入口
- `SubagentExecutor`
- subagent config / registry
- tool filtering
- 并发数量限制

## 推荐实现目标

- 主 agent 可以为一个 bounded task 启动 subagent
- subagent 拥有独立消息上下文
- subagent 工具集默认比主 agent 更窄
- 支持继承或指定 model
- 对并发 subagents 做上限控制

## 推荐落地文件

- `backend/packages/harness/deerflow/subagents/executor.py`
- `backend/packages/harness/deerflow/subagents/registry.py`
- `backend/packages/harness/deerflow/subagents/config.py`
- `backend/packages/harness/deerflow/tools/builtins/task_tool.py`
- `backend/packages/harness/deerflow/agents/middlewares/subagent_limit_middleware.py`

## 推荐的第一版委派模型

第一版可以只支持两类 subagent：

- `general_purpose`
- `bash_agent` 或一个代码执行子代理

关键不是 agent 数量，而是把 delegation contract 做稳定。

## 明确不做

- 不要求一开始就做自治 agent team
- 不要求持久化 mailbox
- 不要求完整 supervisor protocol

## 完成标准

- 主 agent 能清晰地把一个任务委派出去并拿回结果
- subagent 不会无边界地继承父 agent 的所有工具
- 并发上限能防止一次性炸出太多并行任务
- 主 agent 与 subagent 的上下文隔离是可见且可解释的

## 核心学习点

- scale 不只是“更多 token”，而是“更好的任务隔离”
- subagent 的本质价值是缩小上下文和职责，不是制造花哨并行
- delegation contract 一旦设计好，后面的 runtime services 与 frontend 才有稳定对象可展示

## 对应 DeerFlow 2.0 模块

- `backend/packages/harness/deerflow/subagents/*`
- `backend/packages/harness/deerflow/tools/builtins/task_tool.py`
- `backend/packages/harness/deerflow/agents/middlewares/subagent_limit_middleware.py`

## 推荐公开 demo

- 一个 prompt：主 agent 把“调研”和“生成代码”分给两个子任务
- 一张图：`lead_agent -> task_tool -> SubagentExecutor -> result`
- 一段说明：为什么 delegation 首先是上下文优化，而不是吞吐优化

## 进入下一阶段前必须确认

- 委派边界已经稳定
- subagent 工具过滤已生效
- 你已经准备补上真正产品级需要的 runtime services

