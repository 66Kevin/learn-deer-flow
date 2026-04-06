from __future__ import annotations

import unittest

from langgraph.graph.state import CompiledStateGraph

from tests.p02_tool_dispatch.support import REPO_ROOT, ensure_p02_harness_on_path

ensure_p02_harness_on_path()

from mini_deerflow.agents import make_lead_agent  # type: ignore  # noqa: E402


class TestP02LeadAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.config_path = REPO_ROOT / "tests" / "fixtures" / "p02-config.yaml"

    def test_make_lead_agent_runs_model_tools_model_loop(self) -> None:
        agent = make_lead_agent(
            config={"configurable": {"config_path": str(self.config_path)}}
        )

        self.assertIsInstance(agent, CompiledStateGraph)
        result = agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": "what time is it and search P02"}
                ]
            }
        )

        self.assertEqual(result["messages"][-1].type, "ai")
        self.assertIn("P02 final answer", result["messages"][-1].content)
        self.assertIn(
            "search_stub=query=P02; results=Mini DeerFlow P02 search result",
            result["messages"][-1].content,
        )

        tool_messages = [
            message
            for message in result["messages"]
            if getattr(message, "type", "") == "tool"
        ]
        self.assertEqual(
            [message.name for message in tool_messages], ["current_time", "search_stub"]
        )

    def test_make_lead_agent_respects_runtime_tool_groups(self) -> None:
        agent = make_lead_agent(
            config={
                "configurable": {
                    "config_path": str(self.config_path),
                    "tool_groups": ["web"],
                }
            }
        )

        result = agent.invoke({"messages": [{"role": "user", "content": "search P02"}]})
        tool_messages = [
            message
            for message in result["messages"]
            if getattr(message, "type", "") == "tool"
        ]

        self.assertEqual([message.name for message in tool_messages], ["search_stub"])
        self.assertNotIn("current_time=", result["messages"][-1].content)


if __name__ == "__main__":
    unittest.main()
