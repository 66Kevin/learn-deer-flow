



DeerFlow 2.0 的官方定位直接把自己描述为harness

它不是需要用户自行“拼装”的 framework，而是提供文件系统、sandbox、skills、memory、sub-agents 等能力的“让 agents 把事情做完的运行时基础设施”，并且在代码结构上将可复用的 “harness包（deerflow.*）” 与具体应用层（FastAPI Gateway 等）严格隔离。

DeerFlow把 harness 的核心职责拆解为：

- 生命周期管理（thread/sandbox）
- 控制流(middleware chain)
- 接口编排（tools/MCP）
- 能力模块化(skills)
- 状态与记忆持久化（state/memory）
- 安全治理（guardrails）

在**生命周期管理**上，thread（会话线程）是隔离与生命周期管理的基本单位。DeerFlow 会为每个 thread 创建本地目录树（.deer-flow/threads/{thread_id}/user-data/...），并向 agent 暴露稳定的虚拟路径（如 /mnt/user-data/{workspace,uploads,outputs}、/mnt/skills），再由路径替换函数把虚拟路径映射到真实宿主路径或容器挂载路径。 这类“虚拟路径 + 真实路径”的抽象，是典型 harness 技术：它让上层逻辑不绑定部署形态（本地/容器/K8s），同时也为测试与回放提供了稳定接口（不随机器路径变化）。

在**控制流**方面，Lead Agent 通过严格顺序的 middleware chain 把“agent 推理”包裹在一系列可控的横切能力中：线程数据目录管理、上传文件注入、sandbox 获取、工具调用修复、工具调用授权（guardrails）、历史摘要压缩、任务清单、标题生成、长期记忆更新、图片注入、子代理并发限制以及澄清中断等。 这种 middleware 化的“可插拔控制面”就是 harness 的工程化实现方式：把复杂系统行为拆成可组合的、可测试的、可替换的控制点。

在**接口编排**层面，工具系统（tools）把多个来源的能力统一成 agent 可调用的工具集合：包括 sandbox 工具（bash、ls、read_file、write_file、str_replace 等）、内置工具（present_files、ask_clarification、view_image）、配置定义的工具、以及 MCP 工具与社区工具。 其中 MCP（Model Context Protocol）是把“外部系统/工具”接入 agent 的标准化接口：MCP 官方把它定义为一种开源标准，用于连接 AI 应用与外部数据源、工具和工作流；DeerFlow 侧则通过多服务器客户端、缓存与传输协议（stdio/SSE/HTTP）以及 OAuth token flow 支持，把 MCP 工具纳入统一工具面。 在 harness 语境里，这相当于把“可替换的外设（USB-C）”变成 agent runtime 的一部分，但仍可由策略层（guardrails）与 sandbox 边界约束其风险。

在**能力模块化**层面，skills 系统把复杂工作流写成结构化的 SKILL.md（YAML frontmatter + Markdown body），可包含脚本、参考资料与资产，并可按需渐进加载（只有任务需要时才加载，以控制上下文开销）。 skills 能通过 Gateway 安装 .skill 压缩包并在 system prompt 中注入启用列表与容器路径，这让 harness 不仅提供“工具”，还提供“可复用工作流模板”。

在**状态与记忆**层面，配置示例明确列出 summarization（触发条件与保留策略）、memory（memory.json、debounce_seconds、max_facts、注入开关与 token 上限）、以及 embedded client 的 checkpointer（memory/sqlite/postgres）等机制，用于保证长链路任务的可持续运行与可复现。 

在**可观测性**上，官方 README 给出了 LangSmith 与 Langfuse 的 tracing 开关与环境变量配置，并指出两者可同时启用；当 provider 启用但缺凭据或初始化失败时会 fail fast。 

这些能力共同构成了一个典型 harness 的闭环：控制（middleware/策略）—执行（tools/sandbox）—状态（thread/checkpoint/memory）—观测（tracing）—产物（outputs/artifacts）
