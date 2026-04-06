from __future__ import annotations

import os
import unittest

from tests.p02_tool_dispatch.support import P02_BACKEND_ROOT, ensure_p02_harness_on_path

ensure_p02_harness_on_path()

from mini_deerflow.models.factory import create_chat_model  # type: ignore  # noqa: E402


class TestP02ExampleConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.config_path = P02_BACKEND_ROOT / "config.example.yaml"
        self.original_api_key = os.environ.get("DEEPSEEK_API_KEY")
        os.environ["DEEPSEEK_API_KEY"] = "test-key"

    def tearDown(self) -> None:
        if self.original_api_key is None:
            os.environ.pop("DEEPSEEK_API_KEY", None)
        else:
            os.environ["DEEPSEEK_API_KEY"] = self.original_api_key

    def test_example_config_can_create_default_chat_model(self) -> None:
        model = create_chat_model(config_path=self.config_path)
        self.assertEqual(type(model).__name__, "ChatOpenAI")
        self.assertEqual(model.model_name, "deepseek-reasoner")
        self.assertEqual(model.openai_api_base, "https://api.deepseek.com")
        self.assertEqual(model.openai_api_key.get_secret_value(), "test-key")


if __name__ == "__main__":
    unittest.main()
