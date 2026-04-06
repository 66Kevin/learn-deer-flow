from __future__ import annotations

import unittest
from pathlib import Path


P02_ROOT = Path(__file__).resolve().parents[2] / "P02-tool-dispatch"


class TestP02Readme(unittest.TestCase):
    def test_readme_mentions_finished_stage_guidance(self) -> None:
        readme = (P02_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("backend/langgraph.json", readme)
        self.assertIn("make_lead_agent()", readme)
        self.assertIn("create_chat_model()", readme)
        self.assertIn("get_available_tools()", readme)
        self.assertIn("tool_groups", readme)
        self.assertIn("tools", readme)
        self.assertIn("langgraph dev", readme)
        self.assertIn("real YAML", readme)
        self.assertIn("current_time", readme)
        self.assertIn("echo", readme)
        self.assertIn("search_stub", readme)
        self.assertIn("sandbox", readme)
        self.assertIn("MCP", readme)


if __name__ == "__main__":
    unittest.main()
