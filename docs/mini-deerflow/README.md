# Mini DeerFlow

这套文档面向已经具备 `LangChain` / `LangGraph` 基础、希望系统拆解 `DeerFlow 2.0` 的读者。

目标不是一次性复刻全部细节，而是沿着 `P01 -> P11` 的顺序，把 `DeerFlow 2.0` 的核心分层逐步重建出来：`lead_agent`、tools、thread state、middleware、planning、skills、context compact、sandbox、subagents、runtime services、product shell。

建议阅读顺序：

- [P00 Roadmap](./P00-roadmap.md)
- [P01 The Loop](./P01-the-loop.md)
- [P02 Tool Dispatch](./P02-tool-dispatch.md)
- [P03 Thread State](./P03-thread-state.md)
- [P04 Middleware](./P04-middleware.md)
- [P05 Planning](./P05-planning.md)
- [P06 Skills](./P06-skills.md)
- [P07 Context Compact](./P07-context-compact.md)
- [P08 Sandbox](./P08-sandbox.md)
- [P09 Subagents](./P09-subagents.md)
- [P10 Runtime Services](./P10-runtime-services.md)
- [P11 Product Shell](./P11-product-shell.md)

文档约定：

- 中文为主，特有名词保留英文原词。
- 以 `DeerFlow 2.0` 为主要参考，而不是 `1.x Deep Research workflow`。
- 每个阶段都必须有清晰边界、可运行产物、可演示结果、可进入下一阶段的完成标准。

