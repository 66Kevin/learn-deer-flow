from __future__ import annotations

import unittest
from pathlib import Path


P02_ROOT = Path(__file__).resolve().parents[2] / "P02-tool-dispatch"


class TestP02Readme(unittest.TestCase):
    def test_readme_documents_runnable_stage_contract(self) -> None:
        readme = (P02_ROOT / "README.md").read_text(encoding="utf-8")

        expected_fragments = [
            "backend/langgraph.json",
            "make_lead_agent()",
            "create_chat_model()",
            "get_available_tools()",
            "tool_groups",
            "tools",
            "builtin tools live in code",
            "configured tools are loaded from `config.example.yaml`",
            "current_time",
            "echo",
            "search_stub",
            "DEEPSEEK_API_KEY",
            "PYTHONPATH=. uv run --project P02-tool-dispatch/backend --with pytest python -m pytest tests/p02_tool_dispatch -v",
            "python3 -m compileall P02-tool-dispatch/backend",
            "sandbox",
            "MCP",
        ]

        for fragment in expected_fragments:
            self.assertIn(fragment, readme)


if __name__ == "__main__":
    unittest.main()
