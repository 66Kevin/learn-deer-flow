from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

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

    def test_get_available_tools_raises_clear_error_for_bad_provider_path(self) -> None:
        config_text = """
models:
  - name: fake-tool-model
    display_name: Fake Tool Model
    use: mini_deerflow.models.testing:ToolCallingChatModel
    model: tool-calling

tool_groups:
  - name: builtin
  - name: web

tools:
  - name: broken_search
    group: web
    use: mini_deerflow.community.missing.tools:missing_tool
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "bad-provider.yaml"
            config_path.write_text(config_text, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, r"broken_search.*mini_deerflow\.community\.missing\.tools:missing_tool"):
                get_available_tools(config_path=config_path)


if __name__ == "__main__":
    unittest.main()
