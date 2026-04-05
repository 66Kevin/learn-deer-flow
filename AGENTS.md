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

**CRITICAL: Always update README.md and AGENTS.md after every code change**

When making code changes, you MUST update the relevant documentation:

- Update `README.md` for user-facing changes such as features, setup, and usage instructions
- Update `AGENTS.md` for development changes such as architecture, commands, workflows, and internal systems
- Keep documentation synchronized with the codebase at all times
- Ensure accuracy and timeliness of all documentation

## Architecture

## Runtime Environment

- Dependency manager: `uv`
- Python version: `python3.13`

常用启动方式：

```bash
cd P01-the-loop/backend
uv sync
uv run langgraph dev
```


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
