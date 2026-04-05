from __future__ import annotations

import unittest
from pathlib import Path

from tests.p01_the_loop.support import P01_BACKEND_ROOT


class TestP01Layout(unittest.TestCase):
    def test_stage_layout_has_minimal_backend_entrypoints(self) -> None:
        self.assertTrue((P01_BACKEND_ROOT / "langgraph.json").exists())
        self.assertTrue((P01_BACKEND_ROOT / "pyproject.toml").exists())
        self.assertTrue((P01_BACKEND_ROOT / "config.example.yaml").exists())


if __name__ == "__main__":
    unittest.main()

