# P10 Runtime Services

> memory, uploads, artifacts, API

## 本阶段目标

补上一个“能长期使用”的 harness 还缺的服务层：`memory`、`uploads`、`artifacts`、`checkpointer`、`stream bridge`、最小 `Gateway API`。

这一阶段开始把系统从“会跑”推进到“能被产品壳层持续消费”。

## 架构范围

本阶段新增：

- thread persistence / checkpointer
- memory storage 与 updater
- uploads manager
- artifacts catalog / serving
- run / stream bridge
- 最小 gateway endpoints

## 推荐实现目标

- thread 在重启后仍可恢复
- 用户上传的文件能进入 thread workspace
- agent 生成的 `outputs` 能被 catalog 化并对外提供
- memory facts 能异步更新，而不是阻塞主响应
- Gateway 至少提供 `threads/uploads/artifacts/models` 的最小 API

## 推荐落地文件

- `backend/packages/harness/deerflow/agents/checkpointer/*`
- `backend/packages/harness/deerflow/agents/memory/*`
- `backend/packages/harness/deerflow/uploads/*`
- `backend/packages/harness/deerflow/runtime/stream_bridge/*`
- `backend/packages/harness/deerflow/runtime/runs/*`
- `backend/app/gateway/*`

## 推荐边界切法

本阶段建议坚持一个原则：先把服务层对象和接口建好，再决定前端如何消费。

也就是说，`memory`、`artifacts`、`uploads`、`runs` 应该先成为 backend 的明确概念，等到 `P11` 再把它们做成完整 UI。

## 明确不做

- 不把所有 UI 一次性补上
- 不把 MCP 管理提前放进本阶段
- 不强求一开始就具备完整设置页

## 完成标准

- thread state 可以持久化
- uploads 与 outputs 都有明确生命周期和目录归属
- artifacts 可以被 API 层发现和读取
- memory 更新不阻塞主执行链
- 最小 Gateway API 可以为前端提供真实数据而不是 mock

## 核心学习点

- runtime services 是 harness 真正走向产品化的支撑层
- `memory` 和 `context compact` 是两层不同问题
- `uploads`、`artifacts`、`runs` 一旦成为正式服务对象，前端和 observability 都会容易很多

## 对应 DeerFlow 2.0 模块

- `backend/packages/harness/deerflow/agents/memory/*`
- `backend/packages/harness/deerflow/agents/checkpointer/*`
- `backend/packages/harness/deerflow/uploads/*`
- `backend/packages/harness/deerflow/runtime/*`
- `backend/app/gateway/*`

## 推荐公开 demo

- 上传一个文件，agent 处理后生成 artifact，再通过 API 读取
- 重启服务后恢复同一个 thread
- 一张图：`thread state + uploads + artifacts + memory + checkpointer`

## 进入下一阶段前必须确认

- 服务层对象已经独立成型
- 前端不再需要大量 mock 数据
- 你已经具备拼装完整 product shell 的 backend 基础

