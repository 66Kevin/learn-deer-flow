# P11 Product Shell

> streaming, MCP, frontend, proxy

## 本阶段目标

把前面的 harness 与 runtime services 封装成一个真正可用的本地产品：有 `Frontend`、有 `Gateway API`、有 `LangGraph Server`、有统一入口、支持 `MCP` 配置和实时 streaming。

到这一阶段结束，学习版就应该能让用户从浏览器直接体验核心 DeerFlow 2.0 思路。

## 架构范围

本阶段新增：

- `Frontend` 聊天与工作区 UI
- streaming message rendering
- `Gateway API` 与 `LangGraph Server` 的前端消费路径
- `MCP` 配置与工具发现入口
- `Proxy` 或统一入口层

## 推荐实现目标

- 浏览器可通过单入口访问系统
- 能看到实时 streaming 回复
- 能查看 todo、artifacts、uploads、thread history
- 能在界面上切换 model、查看 skills、启用或检查 MCP 工具
- 前后端与 agent runtime 的边界清晰，不把业务状态硬塞回 harness core

## 推荐落地文件

- `frontend/src/app/*`
- `frontend/src/components/workspace/*`
- `frontend/src/components/ai-elements/*`
- `backend/app/gateway/routers/*`
- `backend/packages/harness/deerflow/mcp/*`
- `docker/*` 或统一 proxy 配置

## 关于 MCP

在这条路线里，`MCP` 放在 `P11` 而不是更早，是因为学习版前面更需要先讲清：

- tool system 自身怎么工作
- runtime services 如何支撑可用产品

等到这些都稳定后，再引入 `MCP`，读者更容易看懂它是“扩展工具面”的协议层，而不是“另一个神秘工具源”。

## 明确不做

- 不强求一开始就做全部 `IM channels`
- 不强求追平上游所有设置页与运营能力
- 不强求完全一致的视觉与交互细节

如果后续想继续追平 DeerFlow 2.0，可以把 `IM channels`、更复杂 deployment、更多 observability 与社区集成放到 `P11+`。

## 完成标准

- `localhost` 下存在统一入口
- 用户可以从浏览器发起真实对话而不是 mock
- streaming、uploads、artifacts、thread history 都能在 UI 中看到
- 至少有一个 `MCP` 工具源可被配置或展示
- 整体系统已经具备“可分享、可截图、可演示、可吸引 stars”的产品外形

## 核心学习点

- `Product Shell` 不是给 harness “包一层皮”，而是把 runtime 能力变成可交互产品
- `Gateway API` 与 `LangGraph Server` 分层后，前端与 agent runtime 的职责会更清楚
- `Proxy` 的价值不是技术炫技，而是给用户一个稳定、统一的入口

## 对应 DeerFlow 2.0 模块

- `frontend/*`
- `backend/app/gateway/*`
- `backend/packages/harness/deerflow/mcp/*`
- `docker/*`

## 推荐公开 demo

- 一段完整浏览器操作 GIF：提问、streaming、生成 artifact、打开结果
- 一张系统总架构图：`Frontend + Gateway + LangGraph + Harness`
- 一张路线闭环图：`P01 -> P11`

## 结束时应该达到的状态

到 `P11` 结束，`mini-deerflow` 不一定完全等于上游 DeerFlow 2.0，但应该已经覆盖它最有教学价值的系统主线：

- `lead_agent`
- `middleware`
- `tools`
- `skills`
- `context compact`
- `sandbox`
- `subagents`
- `memory / uploads / artifacts / API`
- `frontend / MCP / proxy`

这时再去补 parity 细节，成本会低很多，因为读者已经真正理解这套系统是如何一层层长出来的。

