from __future__ import annotations

from typing import Any

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from mini_deerflow.agents.lead_agent.prompt import get_system_prompt
from mini_deerflow.models.factory import create_chat_model
from mini_deerflow.tools import get_available_tools


def _extract_runtime_options(config: Any) -> dict[str, Any]:
    if not isinstance(config, dict):
        return {}

    configurable = config.get("configurable")
    if not isinstance(configurable, dict):
        return {}

    return configurable


def _select_next_node(state: MessagesState) -> str:
    messages = state.get("messages", [])
    if not messages:
        return END

    last_message = messages[-1]
    tool_calls = getattr(last_message, "tool_calls", None)
    if isinstance(tool_calls, list) and tool_calls:
        return "run_tools"

    return END


def make_lead_agent(config: dict[str, Any] | None = None) -> Any:
    """Build the minimal lead agent for P02."""

    runtime_options = _extract_runtime_options(config)
    model_name = runtime_options.get("model_name")
    config_path = runtime_options.get("config_path")
    tool_groups = runtime_options.get("tool_groups")

    model = create_chat_model(name=model_name, config_path=config_path)
    tools = get_available_tools(config_path=config_path, groups=tool_groups)
    bound_model = model.bind_tools(tools)
    tool_node = ToolNode(tools)
    system_prompt = get_system_prompt()

    def call_model(state: MessagesState) -> dict[str, list[Any]]:
        messages = state.get("messages", [])
        response = bound_model.invoke([SystemMessage(content=system_prompt), *messages])
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("call_model", call_model)
    graph.add_node("run_tools", tool_node)
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
