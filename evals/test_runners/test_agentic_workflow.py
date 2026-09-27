"""Test runner for agentic workflow, reflection loops, and iterative refinement."""

import pytest
from langgraph.graph.state import CompiledStateGraph

from app.graph.state import TweetState
from evals.golden_set import EvalType, GoldenTestCase, load_dataset
from evals.metrics import compute_constraint_adherence


@pytest.mark.llm
class TestAgenticWorkflowEvaluation:
    """Evaluate multi-step reflection effectiveness, self-correction, and iteration limits."""

    @pytest.mark.parametrize(
        "test_case",
        load_dataset(EvalType.AGENTIC_WORKFLOW),
        ids=lambda tc: tc.id,
    )
    def test_reflection_improvement_and_convergence(
        self, graph: CompiledStateGraph, test_case: GoldenTestCase
    ) -> None:
        """Verify that reflection converges within max_attempts and refines tweet output."""
        state: TweetState = {
            "user_query": test_case.query,
            "max_attempts": 3,
            "reflection_enabled": True,
        }
        result = graph.invoke(state)

        # Ensure execution terminated safely
        assert result["final_status"] in ["SUCCESS", "MAX_ATTEMPTS_REACHED"]
        assert result["attempt"] >= 1
        assert result["attempt"] <= 3

        # Deterministic constraint verification on final output
        final_tweet = result.get("tweet", "")
        compliance = compute_constraint_adherence(
            prediction=final_tweet,
            must_include=test_case.must_include,
            forbidden_words=test_case.forbidden_words,
            max_char_limit=test_case.max_char_limit,
        )

        assert compliance["length_passed"] is True, f"Length constraint violated: {compliance['char_count']} chars"
        assert compliance["forbidden_passed"] is True, f"Forbidden words found: {compliance['found_forbidden']}"
