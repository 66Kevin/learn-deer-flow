# P00 Roadmap

## 这套路线在解决什么问题

`DeerFlow 2.0` 的核心不是一个“大而全的 research graph”，而是一个可扩展的 `super agent harness`。它把 agent 真正需要的运行时能力拆成了几层：

- `lead_agent` 与 model factory
- tool system
- thread state 与 workspace
- middleware chain
- planning / todo tracking
- skills
- context compact
- sandbox
- subagents
- runtime services
- product shell

如果从完整仓库直接读，很容易看到的是模块，难以看到的是“系统为什么长成这样”。`mini-deerflow` 的目标就是把这个成长过程拆成 11 个阶段，让每一阶段都只引入一个新的系统杠杆。

## 目标读者

- 已有 `LangChain` / `LangGraph` 使用经验
- 想理解一个现代 agent harness 为什么要有 `middleware`、`sandbox`、`skills`、`subagents`
- 想从 DeerFlow 2.0 学到可迁移的架构方法，而不是只抄一个项目结构

## 设计原则

- `The loop stays small.` agent loop 尽量不长，复杂性优先外置。
- `One phase, one new system lever.` 每一阶段只引入一个新的核心机制。
- `Map to real DeerFlow 2.0 modules.` 每一阶段都能映射回真实源码模块。
- `Every phase must demo well.` 每一阶段都应该能做成文章、截图、GIF 或 trace。
- `Delay product complexity.` 前期先学 harness core，后期再补 `Gateway`、`Frontend`、`Proxy`。

## 最终目标架构

```text
Browser / Demo UI
        |
        v
Proxy / Unified Entry
   |            |
   v            v
Frontend     Gateway API
                 |
                 v
          LangGraph Server
                 |
                 v
            lead_agent
                 |
   +------+------+------+------+------+
   |      |      |      |      |      |
 tools  skills sandbox memory subagents runtime services
```

## 推荐最终目录形态

为了降低与 `DeerFlow 2.0` 对照时的心智成本，学习版建议尽量保留上游命名：

```text
backend/
  langgraph.json
  packages/harness/deerflow/
    agents/
    tools/
    sandbox/
    skills/
    subagents/
    models/
    runtime/
    config/
  app/
    gateway/
frontend/
skills/
docs/
scripts/
```

如果为了教学可读性需要临时简化，也建议优先简化实现，不要频繁改名。

## 分阶段总览


| Phase | 核心问题                       | 新增能力                           | 对应 DeerFlow 2.0 重点                |
| ----- | ------------------------------ | ---------------------------------- | ------------------------------------- |
| `P01` | 最小 agent runtime 是什么      | `lead_agent + model`               | `agents/lead_agent`, `models/factory` |
| `P02` | tool 为什么能插拔              | tool registry / dispatch           | `tools/*`, `tool_config`              |
| `P03` | 为什么每次运行都要有 workspace | thread state / thread data         | `thread_state`, `paths`               |
| `P04` | cross-cutting concern 放哪     | middleware chain                   | `agents/middlewares/*`                |
| `P05` | 复杂任务如何保持方向感         | planning / todos                   | `TodoMiddleware`, plan mode           |
| `P06` | 领域知识怎么按需注入           | skill loading                      | `skills/*`                            |
| `P07` | 长会话为什么不会马上死掉       | summarization / compact            | `SummarizationMiddleware`             |
| `P08` | 为什么执行必须有边界           | sandbox                            | `sandbox/*`, `aio_sandbox/*`          |
| `P09` | 一个 agent 为什么不够          | subagents / delegation             | `subagents/*`, `task_tool`            |
| `P10` | 产品级运行时还缺什么           | memory / uploads / artifacts / API | `memory/*`, `runtime/*`, `gateway/*`  |
| `P11` | 怎样变成完整可用产品           | streaming / MCP / frontend / proxy | `frontend/*`, `mcp/*`, `docker/*`     |

## 推荐阶段边界

这套路线故意不按“功能清单”推进，而按“系统边界”推进：

- `P01-P04` 是 harness core
- `P05-P07` 是 agent capability management
- `P08-P09` 是 execution scaling
- `P10-P11` 是 productization

这样做的好处是，读者在每个阶段都能回答一个明确问题：

- agent loop 本身有多小
- tool / state / middleware 为什么要从 loop 中分离
- planning、skills、compact 为什么是运行时能力，不是业务分支
- sandbox、subagents、runtime services 为什么是 harness 进入“可用”阶段的分水岭

## 全局完成标准

每个阶段都建议满足这 6 条：

- 有一个清晰的 `in scope` / `out of scope` 边界
- 至少有一个可以运行的 smoke demo
- 至少有一个可以公开展示的结果物
- 与上一阶段相比只引入一个新的主要系统概念
- 与 `DeerFlow 2.0` 源码存在明确映射
- 为下一阶段留下自然扩展点，而不是推倒重来

## 什么时候算“接近完整 DeerFlow 2.0”

`mini-deerflow` 到 `P11` 结束时，不要求完全追平 DeerFlow 2.0 的所有细节，但应该覆盖它最重要的系统骨架：

- `lead_agent` 作为主 agent runtime
- `middleware` 作为主要扩展点
- `tools + skills + sandbox + subagents` 作为 action surface
- `memory + uploads + artifacts + checkpointer` 作为 runtime services
- `Gateway + Frontend + Proxy + MCP` 作为 product shell

不在这条主线里的能力，例如 `IM channels`、更复杂的 deployment、社区扩展生态，可以在 `P11` 之后作为补充章节或 parity backlog 处理。
