from __future__ import annotations

import unittest
from pathlib import Path

from langgraph.graph.state import CompiledStateGraph

from tests.p01_the_loop.support import REPO_ROOT, ensure_p01_harness_on_path

ensure_p01_harness_on_path()

from deerflow.agents import make_lead_agent  # type: ignore  # noqa: E402


class TestLeadAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.config_path = REPO_ROOT / "tests" / "fixtures" / "p01-config.yaml"

    def test_make_lead_agent_returns_runnable_graph(self) -> None:
        agent = make_lead_agent(
            config={"configurable": {"config_path": str(self.config_path)}}
        )

        self.assertIsInstance(agent, CompiledStateGraph)
        result = agent.invoke({"messages": [{"role": "user", "content": "hello"}]})
        self.assertEqual(result["messages"][-1].type, "ai")
        self.assertEqual(result["messages"][-1].content, "P01 says hello")

    def test_make_lead_agent_uses_requested_model_name(self) -> None:
        agent = make_lead_agent(
            config={
                "configurable": {
                    "config_path": str(self.config_path),
                    "model_name": "fake-alt",
                }
            }
        )

        result = agent.invoke({"messages": [{"role": "user", "content": "hello"}]})
        self.assertEqual(result["messages"][-1].content, "P01 alternate response")


if __name__ == "__main__":
    unittest.main()
