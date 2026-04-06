# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## Project Overview

`learn-deer-flow` 是一个面向学习与拆解的仓库，用来逐步理解并重建一个精简版的 `DeerFlow 2.0`。

当前仓库主要包含两部分内容：

- `docs/`: 学习型文档，当前重点是 `mini-deerflow` 的阶段化说明。
- `P01-the-loop/`: 第一阶段的最小可运行实现，聚焦 `lead_agent`、最小 system prompt、模型工厂与 `langgraph` 入口。

当前阶段强调清晰边界和可运行性，故意不引入完整产品能力，例如 tools、memory、sandbox、frontend 等复杂模块。

## Important Development Guidelines

### Documentation Update Policy

**CRITICAL: Always update the relevant section README and AGENTS.md after every code change**

When making code changes, you MUST update the relevant documentation:

- Update the nearest relevant section README for user-facing changes such as features, setup, and usage instructions
  - For example, changes under `P01-the-loop/` should update `P01-the-loop/README.md`, not the repository root `README.md`, unless the root-level project overview also needs to change
- Update `AGENTS.md` for development changes such as architecture, commands, workflows, and internal systems
- Keep documentation synchronized with the codebase at all times
- Ensure accuracy and timeliness of all documentation

When updating `AGENTS.md`, keep it focused on stable, high-level guidance for AI coding agents:

- Prefer repository-wide conventions, architectural boundaries, and long-lived workflows
- Do not record one-off debugging notes, temporary fixes, exact local ports, or other overly detailed operational steps
- Put stage-specific setup, debugging, and usage details in the nearest section README or docs, not in `AGENTS.md`

## Architecture

## Runtime Environment

- Dependency manager: `uv`
- Python version: `python3.13`

默认开发与调试工作流所需的依赖应包含在项目的默认依赖集合中，避免 README 中的标准命令依赖额外的手动安装步骤。

`P01-the-loop` 的本地实现命名应使用 `mini-deerflow` / `mini_deerflow`，不要把学习版实现直接命名为 `deerflow`；只有在说明与上游 `DeerFlow 2.0` 的对应关系时，才保留对上游项目名的引用。

`P02-tool-dispatch` 的后端基础层延续同样的命名约定，并优先把配置、模型工厂、反射加载这类系统边界放在 `backend/packages/harness/mini_deerflow/` 下的独立模块中，而不是直接塞回 agent 入口。

`P02-tool-dispatch` 中的工具注册表、builtin tools 与 community tool providers 应保留在 `backend/packages/harness/mini_deerflow/tools/` 与 `backend/packages/harness/mini_deerflow/community/` 这些独立边界内，而不是散落到 lead agent 或 graph 入口文件里。

阶段设计文档应放在 `docs/mini-deerflow/spec/`；阶段 implementation plan 应放在独立的 plan 目录中，除非用户另行指定。

`config.yaml` 与 `config.example.yaml` 的新增或更新示例应使用真实 YAML 写法，不要在 `.yaml` 文件中继续新增 JSON-shaped 示例。

## Code Style Guidelines

### Linting and Formatting

- Uses `ruff` for linting and formatting

### Style Guidelines

* **Line length**: 240 characters maximum
* **Python version**: 3.12+ features allowed
* **Type hints**: Use type hints for function signatures
* **Quotes**: Double quotes for strings
* **Indentation**: 4 spaces (no tabs)
* **Imports**: Group by standard library, third-party, local
* **Folder Structure**: When documenting file or directory hierarchies in Markdown, use tree-style guides such as \`├──\`, \`│\`, and \`└──\` to make same-level and parent-child relationships visually clear

### Docstrings

Use docstrings for public functions and classes:

```python
def create_chat_model(name: str, thinking_enabled: bool = False) -> BaseChatModel:
    """Create a chat model instance from configuration.

    Args:
        name: The model name as defined in config.yaml
        thinking_enabled: Whether to enable extended thinking

    Returns:
        A configured LangChain chat model instance

    Raises:
        ValueError: If the model name is not found in configuration
    """
    ...
```

## Documents
