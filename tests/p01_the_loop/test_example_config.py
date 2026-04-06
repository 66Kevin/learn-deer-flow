from __future__ import annotations

import os
import unittest

from tests.p01_the_loop.support import P01_BACKEND_ROOT, ensure_p01_harness_on_path

ensure_p01_harness_on_path()

from mini_deerflow.models.factory import create_chat_model  # type: ignore  # noqa: E402


class TestP01ExampleConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.config_path = P01_BACKEND_ROOT / "config.example.yaml"
        self.original_api_key = os.environ.get("DEEPSEEK_API_KEY")
        os.environ["DEEPSEEK_API_KEY"] = "test-key"

    def tearDown(self) -> None:
        if self.original_api_key is None:
            os.environ.pop("DEEPSEEK_API_KEY", None)
        else:
            os.environ["DEEPSEEK_API_KEY"] = self.original_api_key

    def test_example_config_can_create_default_chat_model(self) -> None:
        model = create_chat_model(config_path=self.config_path)
        self.assertIsNotNone(model)


if __name__ == "__main__":
    unittest.main()
