from __future__ import annotations

import unittest

from tests.p02_tool_dispatch.support import REPO_ROOT, ensure_p02_harness_on_path

ensure_p02_harness_on_path()

from mini_deerflow.config import load_app_config  # type: ignore  # noqa: E402
from mini_deerflow.config.model_config import ModelConfig  # type: ignore  # noqa: E402
from mini_deerflow.models.factory import create_chat_model  # type: ignore  # noqa: E402


class TestP02ToolConfig(unittest.TestCase):
    def setUp(self) -> None:
        fixtures_root = REPO_ROOT / "tests" / "fixtures"
        self.config_path = fixtures_root / "p02-config.yaml"
        self.invalid_group_path = fixtures_root / "p02-invalid-group.yaml"
        self.missing_use_path = fixtures_root / "p02-missing-tool-use.yaml"

    def test_load_app_config_reads_tool_groups_and_tools(self) -> None:
        config = load_app_config(self.config_path)
        self.assertEqual([group.name for group in config.tool_groups], ["builtin", "web"])
        self.assertEqual(config.tools[0].name, "search_stub")
        self.assertEqual(config.tools[0].group, "web")

    def test_load_app_config_rejects_unknown_tool_group(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown tool group"):
            load_app_config(self.invalid_group_path)

    def test_load_app_config_rejects_tool_without_use(self) -> None:
        with self.assertRaisesRegex(ValueError, "Tool config must define `use`"):
            load_app_config(self.missing_use_path)

    def test_model_config_rejects_invalid_required_fields_and_boolean_flags(self) -> None:
        with self.assertRaisesRegex(ValueError, "Model config must define `name`"):
            ModelConfig.from_dict({"name": 123, "use": "module:Model", "model": "demo"})

        with self.assertRaisesRegex(ValueError, "Model config must define `use`"):
            ModelConfig.from_dict({"name": "demo", "use": None, "model": "demo"})

        with self.assertRaisesRegex(ValueError, "Model config must define `model`"):
            ModelConfig.from_dict({"name": "demo", "use": "module:Model", "model": ["bad"]})

        with self.assertRaisesRegex(ValueError, "Model config field `supports_thinking` must be a boolean"):
            ModelConfig.from_dict({"name": "demo", "use": "module:Model", "model": "demo", "supports_thinking": "yes"})

        with self.assertRaisesRegex(ValueError, "Model config field `supports_vision` must be a boolean"):
            ModelConfig.from_dict({"name": "demo", "use": "module:Model", "model": "demo", "supports_vision": 1})

    def test_create_chat_model_uses_default_tool_model(self) -> None:
        model = create_chat_model(config_path=self.config_path)
        self.assertEqual(model.__class__.__name__, "ToolCallingChatModel")


if __name__ == "__main__":
    unittest.main()
