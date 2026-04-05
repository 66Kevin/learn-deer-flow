from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from deerflow.agents.lead_agent.prompt import get_system_prompt
from deerflow.models.factory import create_chat_model


def _normalize_message(message: Any) -> dict[str, Any]:
    if isinstance(message, dict):
        role = message.get("role", "assistant")
        content = message.get("content", "")
        return {"role": role, "content": content}
    if hasattr(message, "role") and hasattr(message, "content"):
        return {"role": getattr(message, "role"), "content": getattr(message, "content")}
    if hasattr(message, "type") and hasattr(message, "content"):
        return {"role": getattr(message, "type"), "content": getattr(message, "content")}
    return {"role": "assistant", "content": str(message)}


def _normalize_messages(messages: Any) -> list[dict[str, Any]]:
    if not isinstance(messages, list):
        return []
    return [_normalize_message(message) for message in messages]


def _extract_runtime_options(config: Any) -> dict[str, Any]:
    if not isinstance(config, dict):
        return {}
    configurable = config.get("configurable")
    if not isinstance(configurable, dict):
        return {}
    return configurable


@dataclass(slots=True)
class SimpleLeadAgent:
    """Small fallback agent for local tests when LangChain is unavailable."""

    model: Any
    system_prompt: str

    def invoke(self, state: dict[str, Any]) -> dict[str, Any]:
        messages = _normalize_messages(state.get("messages", []))
        response = self._invoke_model(messages)
        return {"messages": [*messages, response]}

    def _invoke_model(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        if not hasattr(self.model, "invoke"):
            raise TypeError("Configured model must define an invoke() method.")

        try:
            response = self.model.invoke(messages=messages, system_prompt=self.system_prompt)
        except TypeError:
            try:
                response = self.model.invoke(messages)
            except TypeError:
                response = self.model.invoke(
                    {"messages": messages, "system_prompt": self.system_prompt}
                )

        return _normalize_message(response)


def _build_langchain_agent(model: Any, system_prompt: str) -> Any | None:
    try:
        from langchain.agents import create_agent
    except ImportError:
        return None

    if not hasattr(model, "bind_tools"):
        return None

    return create_agent(
        model=model,
        tools=None,
        system_prompt=system_prompt,
        name="lead_agent",
    )


def make_lead_agent(config: dict[str, Any] | None = None) -> Any:
    """Build the minimal lead agent for P01.

    When LangChain is available and the configured model is a LangChain chat
    model, this returns a real LangChain/LangGraph agent. In lightweight test
    environments it falls back to a tiny local runnable with the same `invoke`
    entrypoint.
    """

    runtime_options = _extract_runtime_options(config)
    model_name = runtime_options.get("model_name")
    config_path = runtime_options.get("config_path")

    model = create_chat_model(name=model_name, config_path=config_path)
    system_prompt = get_system_prompt()

    return _build_langchain_agent(model, system_prompt) or SimpleLeadAgent(
        model=model,
        system_prompt=system_prompt,
    )

