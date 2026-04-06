from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from langgraph.graph.state import CompiledStateGraph

from tests.p02_tool_dispatch.support import REPO_ROOT, ensure_p02_harness_on_path

ensure_p02_harness_on_path()

from mini_deerflow.agents import make_lead_agent  # type: ignore  # noqa: E402


class TestP02LeadAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.config_path = REPO_ROOT / "tests" / "fixtures" / "p02-config.yaml"

    def _write_config(
        self,
        directory: Path,
        name: str,
        *,
        model_name: str,
        final_prefix: str,
        search_query: str,
        search_result: str,
    ) -> Path:
        config_path = directory / name
        config_path.write_text(
            f"""
models:
  - name: {model_name}
    display_name: {model_name}
    use: mini_deerflow.models.testing:ToolCallingChatModel
    model: {model_name}
    final_prefix: {final_prefix}
    search_query: {search_query}

tool_groups:
  - name: builtin
  - name: web

tools:
  - name: search_stub
    group: web
    use: mini_deerflow.community.stub_search.tools:search_stub_tool
    results:
      - {search_result}
""".strip()
            + "\n",
            encoding="utf-8",
        )
        return config_path

    def test_make_lead_agent_runs_model_tools_model_loop_from_invoke_runtime_config(
        self,
    ) -> None:
        agent = make_lead_agent(
            config={
                "configurable": {
                    "config_path": str(self.config_path),
                    "tool_groups": [],
                }
            }
        )

        self.assertIsInstance(agent, CompiledStateGraph)
        result = agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": "what time is it and search P02"}
                ]
            },
            config={
                "configurable": {
                    "config_path": str(self.config_path),
                    "tool_groups": ["builtin", "web"],
                }
            },
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

    def test_make_lead_agent_respects_runtime_tool_groups_at_invoke_time(self) -> None:
        agent = make_lead_agent(
            config={
                "configurable": {
                    "config_path": str(self.config_path),
                }
            }
        )

        result = agent.invoke(
            {"messages": [{"role": "user", "content": "search P02"}]},
            config={"configurable": {"tool_groups": ["web"]}},
        )
        tool_messages = [
            message
            for message in result["messages"]
            if getattr(message, "type", "") == "tool"
        ]

        self.assertEqual([message.name for message in tool_messages], ["search_stub"])
        self.assertNotIn("current_time=", result["messages"][-1].content)

    def test_make_lead_agent_uses_runtime_config_path_and_model_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            alpha_config_path = self._write_config(
                temp_path,
                "alpha.yaml",
                model_name="alpha-model",
                final_prefix="Alpha final answer",
                search_query="alpha-query",
                search_result="Alpha search result",
            )
            beta_config_path = self._write_config(
                temp_path,
                "beta.yaml",
                model_name="beta-model",
                final_prefix="Beta final answer",
                search_query="beta-query",
                search_result="Beta search result",
            )

            agent = make_lead_agent(
                config={
                    "configurable": {
                        "config_path": str(alpha_config_path),
                        "model_name": "alpha-model",
                        "tool_groups": ["web"],
                    }
                }
            )

            alpha_result = agent.invoke(
                {"messages": [{"role": "user", "content": "search alpha"}]}
            )
            self.assertIn("Alpha final answer", alpha_result["messages"][-1].content)
            self.assertIn(
                "search_stub=query=alpha-query; results=Alpha search result",
                alpha_result["messages"][-1].content,
            )

            beta_result = agent.invoke(
                {"messages": [{"role": "user", "content": "search beta"}]},
                config={
                    "configurable": {
                        "config_path": str(beta_config_path),
                        "model_name": "beta-model",
                        "tool_groups": ["web"],
                    }
                },
            )
            self.assertIn("Beta final answer", beta_result["messages"][-1].content)
            self.assertIn(
                "search_stub=query=beta-query; results=Beta search result",
                beta_result["messages"][-1].content,
            )


if __name__ == "__main__":
    unittest.main()
