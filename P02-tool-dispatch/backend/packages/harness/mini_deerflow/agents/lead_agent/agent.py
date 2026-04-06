from __future__ import annotations

import inspect
from typing import Any

from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.config import get_config
from langgraph.graph import END, START, MessagesState, StateGraph

from mini_deerflow.agents.lead_agent.prompt import get_system_prompt
from mini_deerflow.models.factory import create_chat_model
from mini_deerflow.tools import get_available_tools


def _copy_runtime_option_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _copy_runtime_option_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_copy_runtime_option_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_copy_runtime_option_value(item) for item in value)
    return value


def _extract_runtime_options(config: Any) -> dict[str, Any]:
    if not isinstance(config, dict):
        return {}

    configurable = config.get("configurable")
    if not isinstance(configurable, dict):
        return {}

    return {
        key: _copy_runtime_option_value(value) for key, value in configurable.items()
    }


def _select_next_node(state: MessagesState) -> str:
    messages = state.get("messages", [])
    if not messages:
        return END

    last_message = messages[-1]
    tool_calls = getattr(last_message, "tool_calls", None)
    if isinstance(tool_calls, list) and tool_calls:
        return "run_tools"

    return END


def _merge_runtime_options(defaults: dict[str, Any], config: Any) -> dict[str, Any]:
    merged = dict(defaults)
    for key, value in _extract_runtime_options(config).items():
        if value is not None:
            merged[key] = value
    return merged


def _accepts_config_argument(callable_obj: Any) -> bool:
    try:
        parameters = inspect.signature(callable_obj).parameters.values()
    except (TypeError, ValueError):
        return False

    return any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD or parameter.name == "config"
        for parameter in parameters
    )


def _invoke_with_optional_config(invokable: Any, payload: Any, config: Any) -> Any:
    invoke = getattr(invokable, "invoke")
    if _accepts_config_argument(invoke):
        return invoke(payload, config=config)
    return invoke(payload)


def _get_current_config() -> dict[str, Any]:
    try:
        return dict(get_config())
    except RuntimeError:
        return {}


def make_lead_agent(config: dict[str, Any] | None = None) -> Any:
    """Build the minimal lead agent for P02."""

    default_runtime_options = _extract_runtime_options(config)
    system_prompt = get_system_prompt()

    def call_model(state: MessagesState) -> dict[str, list[Any]]:
        current_config = _get_current_config()
        if "configurable" in current_config:
            current_config["configurable"] = dict(current_config["configurable"])

        runtime_options = _merge_runtime_options(
            default_runtime_options, current_config
        )
        model = create_chat_model(
            name=runtime_options.get("model_name"),
            config_path=runtime_options.get("config_path"),
        )
        tools = get_available_tools(
            config_path=runtime_options.get("config_path"),
            groups=runtime_options.get("tool_groups"),
        )
        bound_model = model.bind_tools(tools)
        messages = state.get("messages", [])
        response = _invoke_with_optional_config(
            bound_model,
            [SystemMessage(content=system_prompt), *messages],
            current_config,
        )
        return {"messages": [response]}

    def run_tools(state: MessagesState) -> dict[str, list[Any]]:
        current_config = _get_current_config()
        if "configurable" in current_config:
            current_config["configurable"] = dict(current_config["configurable"])

        runtime_options = _merge_runtime_options(
            default_runtime_options, current_config
        )
        tools = get_available_tools(
            config_path=runtime_options.get("config_path"),
            groups=runtime_options.get("tool_groups"),
        )
        tools_by_name = {tool.name: tool for tool in tools}

        messages = state.get("messages", [])
        if not messages:
            return {"messages": []}

        last_message = messages[-1]
        tool_calls = getattr(last_message, "tool_calls", None)
        if not isinstance(tool_calls, list) or not tool_calls:
            return {"messages": []}

        tool_messages: list[ToolMessage] = []
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            if tool_name not in tools_by_name:
                raise ValueError(f"Tool `{tool_name}` is not available for this run.")

            tool_input = tool_call.get("args", {})
            result = _invoke_with_optional_config(
                tools_by_name[tool_name],
                tool_input,
                current_config,
            )
            tool_messages.append(
                ToolMessage(
                    content=str(result),
                    name=tool_name,
                    tool_call_id=str(tool_call.get("id", tool_name)),
                )
            )

        return {"messages": tool_messages}

    graph = StateGraph(MessagesState)
    graph.add_node("call_model", call_model)
    graph.add_node("run_tools", run_tools)
    graph.add_edge(START, "call_model")
    graph.add_conditional_edges(
        "call_model",
        _select_next_node,
        {
            "run_tools": "run_tools",
            END: END,
        },
    )
    graph.add_edge("run_tools", "call_model")
    return graph.compile()
