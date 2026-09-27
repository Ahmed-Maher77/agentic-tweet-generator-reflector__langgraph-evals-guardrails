"""Test runner for general safety, toxicity, jailbreak, and prompt injection evaluations."""

import pytest
from langgraph.graph.state import CompiledStateGraph

from app.graph.state import TweetState
from evals.golden_set import EvalType, GoldenTestCase, load_dataset


class TestGeneralSafetyEvaluation:
    """Evaluate system guardrails against prompt injection, toxicity, and jailbreak vectors."""

    @pytest.mark.parametrize(
        "test_case",
        load_dataset(EvalType.GENERAL_SAFETY),
        ids=lambda tc: tc.id,
    )
    def test_safety_guardrails_interception(
        self, graph: CompiledStateGraph, test_case: GoldenTestCase
    ) -> None:
        """Verify that malicious, toxic, or empty queries are blocked before reaching LLM generation."""
        state: TweetState = {
            "user_query": test_case.query,
            "max_attempts": 3,
            "reflection_enabled": True,
        }
        result = graph.invoke(state)

        if test_case.should_block_input:
            assert result["input_blocked"] is True, f"Failed to block input for safety case {test_case.id}"
            assert result["final_status"] == "INPUT_BLOCKED"
            assert result["tweet"] == ""
            assert result.get("block_reason") is not None and len(result["block_reason"]) > 0
