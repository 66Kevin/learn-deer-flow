# P06 Skills

> inject domain knowledge on demand

## 本阶段目标

为 harness 增加 `skills` 机制，让 agent 不必把所有领域知识都塞进 system prompt，而是按任务需要加载对应 `SKILL.md`。

这是 `DeerFlow 2.0` 从“有工具的 agent”走向“可扩展 harness”的关键一跳。

## 架构范围

本阶段新增：

- skill discovery
- `SKILL.md` parser
- skill metadata / validation
- progressive loading
- skill content 注入策略

## 推荐实现目标

- 支持从内置目录与自定义目录发现 skills
- skill 只在命中触发条件时加载
- 支持最小 metadata 校验
- agent 能把 skill 作为工作流指南，而不是把整份文档原样复读给用户

## 推荐落地文件

- `backend/packages/harness/deerflow/skills/loader.py`
- `backend/packages/harness/deerflow/skills/parser.py`
- `backend/packages/harness/deerflow/skills/types.py`
- `backend/packages/harness/deerflow/skills/validation.py`
- `skills/<skill-name>/SKILL.md`

## 建议的学习版最小 skill 集

- `research`
- `web-page`
- `report-generation`

这三个就足够覆盖“信息搜集、内容组织、产物生成”三类典型工作流。

## 明确不做

- 不做完整 skill marketplace
- 不做复杂版本兼容策略
- 不做过早的 skill GUI 管理

## 完成标准

- 至少能发现并加载一个内置 skill 与一个自定义 skill
- 未命中的 skill 不会污染默认 prompt
- skill 加载结果可解释、可追踪、可调试
- 一个复杂任务因为 skill 的存在而显著更稳定，而不是只是 prompt 更长

## 核心学习点

- `skills` 的价值不在“多一份文档”，而在“把方法论变成可按需装配的运行时资源”
- progressive loading 是控制 prompt budget 的关键
- skill system 是后续吸引外部贡献者和社区 stars 的重要入口

## 对应 DeerFlow 2.0 模块

- `backend/packages/harness/deerflow/skills/*`
- 根目录 `skills/`

## 推荐公开 demo

- 一个不加载 skill 和加载 skill 的对照任务
- 一个自定义 `SKILL.md` 示例，展示学习者如何扩展系统
- 一张图：`task -> skill match -> load -> inject -> execute`

## 进入下一阶段前必须确认

- 你已经建立“知识按需注入”而不是“全部前置注入”的心智
- skill loader 与 parser 已经成型
- 你知道后面为什么需要 `Context Compact` 来兜住长会话

