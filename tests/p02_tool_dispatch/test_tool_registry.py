from __future__ import annotations

import unittest

from tests.p02_tool_dispatch.support import REPO_ROOT, ensure_p02_harness_on_path

ensure_p02_harness_on_path()

from mini_deerflow.tools import get_available_tools  # type: ignore  # noqa: E402


class TestP02ToolRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.config_path = REPO_ROOT / "tests" / "fixtures" / "p02-config.yaml"

    def test_get_available_tools_returns_builtin_and_configured_tools(self) -> None:
        tools = get_available_tools(config_path=self.config_path)
        self.assertEqual([tool.name for tool in tools], ["current_time", "echo", "search_stub"])

    def test_get_available_tools_filters_by_requested_group(self) -> None:
        tools = get_available_tools(config_path=self.config_path, groups=["web"])
        self.assertEqual([tool.name for tool in tools], ["search_stub"])


if __name__ == "__main__":
    unittest.main()
