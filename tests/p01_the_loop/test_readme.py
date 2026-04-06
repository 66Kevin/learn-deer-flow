from __future__ import annotations

import unittest
from pathlib import Path

from tests.p01_the_loop.support import P01_ROOT


class TestP01Readme(unittest.TestCase):
    def test_readme_mentions_langgraph_entry_and_default_run_steps(self) -> None:
        readme = (P01_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("langgraph dev", readme)
        self.assertIn("make_lead_agent", readme)
        self.assertIn("mini-deerflow", readme)


if __name__ == "__main__":
    unittest.main()
