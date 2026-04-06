from __future__ import annotations

from langchain_core.tools import StructuredTool


def _echo(text: str) -> str:
    return text


echo_tool = StructuredTool.from_function(
    func=_echo,
    name="echo",
    description="Return the provided text unchanged.",
)
