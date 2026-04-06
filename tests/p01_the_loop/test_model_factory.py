from __future__ import annotations

import unittest
from pathlib import Path

from tests.p01_the_loop.support import REPO_ROOT, ensure_p01_harness_on_path

ensure_p01_harness_on_path()

from mini_deerflow.config import load_app_config  # type: ignore  # noqa: E402
from mini_deerflow.models.factory import create_chat_model  # type: ignore  # noqa: E402


class TestModelFactory(unittest.TestCase):
    def setUp(self) -> None:
        self.config_path = REPO_ROOT / "tests" / "fixtures" / "p01-config.yaml"

    def test_load_app_config_reads_first_model_from_yaml(self) -> None:
        config = load_app_config(self.config_path)
        self.assertEqual(config.models[0].name, "fake-default")

    def test_create_chat_model_uses_default_model_when_name_missing(self) -> None:
        model = create_chat_model(config_path=self.config_path)
        self.assertEqual(model.__class__.__name__, "FixedResponseChatModel")

    def test_create_chat_model_uses_named_model_when_requested(self) -> None:
        model = create_chat_model(name="fake-alt", config_path=self.config_path)
        self.assertEqual(getattr(model, "response_text"), "P01 alternate response")


if __name__ == "__main__":
    unittest.main()
