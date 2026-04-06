from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from langchain_core.messages import AIMessage


def _message_type(message: Any) -> str:
    if hasattr(message, "type"):
        return str(getattr(message, "type"))
    if isinstance(message, dict):
        return str(message.get("role", ""))
    return ""


def _message_content(message: Any) -> str:
    if hasattr(message, "content"):
        return str(getattr(message, "content"))
    if isinstance(message, dict):
        return str(message.get("content", ""))
    return str(message)


@dataclass(slots=True)
class ToolCallingChatModel:
    """Deterministic local model used by P02 tests."""

    model: str
    final_prefix: str = "P02 final answer"
    search_query: str = "P02"
    timezone: str = "UTC"
    bound_tool_names: list[str] = field(default_factory=list)

    def bind_tools(self, tools: list[Any]) -> "ToolCallingChatModel":
        return ToolCallingChatModel(
            model=self.model,
            final_prefix=self.final_prefix,
            search_query=self.search_query,
            timezone=self.timezone,
            bound_tool_names=[getattr(tool, "name", "") for tool in tools],
        )

    def invoke(self, messages: Sequence[Any]) -> AIMessage:
        tool_messages = [message for message in messages if _message_type(message) == "tool"]
        if tool_messages:
            summary = "; ".join(
                f"{getattr(message, 'name', 'tool')}={_message_content(message)}"
                for message in tool_messages
            )
            return AIMessage(content=f"{self.final_prefix}: {summary}")

        tool_calls: list[dict[str, Any]] = []
        if "current_time" in self.bound_tool_names:
            tool_calls.append(
                {
                    "id": "call_current_time",
                    "name": "current_time",
                    "args": {"timezone": self.timezone},
                    "type": "tool_call",
                }
            )
        if "search_stub" in self.bound_tool_names:
            tool_calls.append(
                {
                    "id": "call_search_stub",
                    "name": "search_stub",
                    "args": {"query": self.search_query},
                    "type": "tool_call",
                }
            )
        if not tool_calls and "echo" in self.bound_tool_names:
            tool_calls.append(
                {
                    "id": "call_echo",
                    "name": "echo",
                    "args": {"text": "P02 echo fallback"},
                    "type": "tool_call",
                }
            )

        if not tool_calls:
            return AIMessage(content=f"{self.final_prefix}: no tools requested")

        return AIMessage(content="", tool_calls=tool_calls)
