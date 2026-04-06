from __future__ import annotations

import unittest

from tests.p02_tool_dispatch.support import P02_BACKEND_ROOT


class TestP02Layout(unittest.TestCase):
    def test_stage_layout_has_tool_dispatch_entrypoints(self) -> None:
        self.assertTrue((P02_BACKEND_ROOT / "langgraph.json").exists())
        self.assertTrue((P02_BACKEND_ROOT / "pyproject.toml").exists())
        self.assertTrue((P02_BACKEND_ROOT / "config.example.yaml").exists())
        self.assertTrue((P02_BACKEND_ROOT / "packages" / "harness" / "mini_deerflow").exists())

    def test_langgraph_entry_uses_mini_deerflow_namespace(self) -> None:
        langgraph_config = (P02_BACKEND_ROOT / "langgraph.json").read_text(encoding="utf-8")
        self.assertIn("mini_deerflow.agents:make_lead_agent", langgraph_config)


if __name__ == "__main__":
    unittest.main()
