"""Test runner for agent tool calling and search decision evaluation with local Ollama LLM."""

import pytest
from langchain_core.language_models.chat_models import BaseChatModel

from app.agents.writer import run_writer_agent
from evals.golden_set import EvalType, GoldenTestCase, load_dataset


@pytest.mark.llm
class TestAgentToolCallingEvaluation:
    """Evaluate single-agent decision-making on whether and how to invoke external tools with real LLM."""

    @pytest.mark.parametrize(
        "test_case",
        load_dataset(EvalType.AGENT_TOOL),
        ids=lambda tc: tc.id,
    )
    def test_agent_tool_decision(
        self,
        test_case: GoldenTestCase,
        ollama_llm: BaseChatModel,
    ) -> None:
        """Verify the agent's autonomous tool-calling logic and execution with real local LLM."""
        search_enabled = bool(test_case.should_use_tool)

        tweet, search_used = run_writer_agent(
            user_query=test_case.query,
            attempt=1,
            max_attempts=3,
            search_enabled=search_enabled,
            llm=ollama_llm,
        )

        assert tweet != "", f"Expected non-empty tweet for test case {test_case.id}"
        if test_case.should_use_tool:
            assert search_used is True, f"Expected search tool to be triggered for: {test_case.query}"
        else:
            assert search_used is False, f"Search should not be triggered for evergreen query: {test_case.query}"
