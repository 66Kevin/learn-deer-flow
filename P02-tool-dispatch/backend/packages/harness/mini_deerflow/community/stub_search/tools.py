from __future__ import annotations

from typing import Sequence

from langchain_core.tools import StructuredTool


def search_stub_tool(name: str = "search_stub", results: Sequence[str] | None = None) -> StructuredTool:
    """Create a deterministic configured search stub tool."""

    resolved_results = ["Mini DeerFlow P02 search result"] if results is None else list(results)

    def _search_stub(query: str) -> str:
        joined_results = " | ".join(resolved_results)
        return f"query={query}; results={joined_results}"

    return StructuredTool.from_function(
        func=_search_stub,
        name=name,
        description="Return deterministic stub search results for testing tool dispatch.",
    )
