# P08 Sandbox

> execution needs a bounded environment

## 本阶段目标

把工具执行从“能不能执行”升级成“在哪里执行、边界是什么、如何隔离”。到这一阶段，学习版才真正开始接近 DeerFlow 2.0 的可用形态。

## 架构范围

本阶段新增：

- `SandboxProvider`
- `Sandbox`
- local sandbox
- 可选的 `aio_sandbox` 或 remote provider
- 虚拟路径映射
- 通过 sandbox 暴露的文件与命令类 tools

## 推荐实现目标

- 定义抽象的 sandbox interface，而不是让 tools 直接碰宿主机
- 默认使用 local sandbox 作为学习版实现
- 让 `workspace/uploads/outputs` 都通过虚拟路径暴露
- 让 `bash/read_file/write_file/ls/str_replace` 等工具走 sandbox interface
- 默认禁止 host-level bash 逃逸

## 推荐落地文件

- `backend/packages/harness/deerflow/sandbox/sandbox.py`
- `backend/packages/harness/deerflow/sandbox/sandbox_provider.py`
- `backend/packages/harness/deerflow/sandbox/local/*`
- `backend/packages/harness/deerflow/sandbox/middleware.py`
- `backend/packages/harness/deerflow/sandbox/tools.py`
- `backend/packages/harness/deerflow/community/aio_sandbox/*`

## 为什么要晚于 P07

一旦接入真正的执行环境，系统复杂度会明显上升。把它放在 `loop / tools / state / middleware / planning / skills / compact` 之后，学习者更容易把注意力放在“边界与隔离”本身，而不是和前面的概念纠缠。

## 明确不做

- 不要求一开始就支持完整 provisioner / Kubernetes
- 不要求一开始就做所有安全策略
- 不要求一开始就追平所有社区 sandbox provider

## 完成标准

- agent 能在 bounded environment 内执行文件与命令类操作
- 生成物会稳定落到 `outputs/`
- 命令执行默认不能越过当前 thread workspace 边界
- tools 的实现依赖 sandbox interface，而不是硬编码宿主机路径

## 核心学习点

- 真正有价值的 agent 执行能力，一定要与执行边界一起设计
- sandbox 是 harness 的一层，不是某个 tool 的附属品
- 虚拟路径映射让 UI、runtime、sandbox 三层能共享同一套路径语义

## 对应 DeerFlow 2.0 模块

- `backend/packages/harness/deerflow/sandbox/*`
- `backend/packages/harness/deerflow/community/aio_sandbox/*`
- `backend/packages/harness/deerflow/sandbox/tools.py`

## 推荐公开 demo

- 一个 prompt：让 agent 在 `outputs/` 生成网页或脚本文件
- 一张图：`virtual path -> physical path`
- 一段说明：为什么“会跑 bash”不重要，“在边界内跑 bash”才重要

## 进入下一阶段前必须确认

- sandbox interface 已经稳定
- 文件/命令 tools 已经真正通过 sandbox 调用
- 你已经准备把“一个 agent 执行”升级成“多个 agent 分工”

