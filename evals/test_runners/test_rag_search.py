"""Test runner for RAG and search grounding evaluations."""

import pytest
from deepeval import assert_test
from langgraph.graph.state import CompiledStateGraph

from app.graph.state import TweetState
from evals.golden_set import EvalType, GoldenTestCase, load_dataset, to_deepeval_test_case
from evals.metrics import get_answer_relevancy_metric, get_hallucination_metric


@pytest.mark.llm
class TestRAGSearchEvaluation:
    """Evaluate grounding, search context integration, and factual fidelity."""

    @pytest.mark.parametrize(
        "test_case",
        load_dataset(EvalType.RAG),
        ids=lambda tc: tc.id,
    )
    def test_search_grounding_fidelity(self, graph: CompiledStateGraph, test_case: GoldenTestCase) -> None:
        """Verify that retrieved search context is properly grounded and not hallucinated."""
        state: TweetState = {
            "user_query": test_case.query,
            "max_attempts": 3,
            "reflection_enabled": True,
            "search_enabled": True,
        }
        result = graph.invoke(state)
        actual_output = result.get("tweet", "")

        assert actual_output != "", f"Empty tweet generated for {test_case.id}"

        context = [test_case.trusted_context] if test_case.trusted_context else []
        deepeval_case = to_deepeval_test_case(test_case, actual_output, retrieval_context=context)

        hallucination = get_hallucination_metric(threshold=0.50)
        relevancy = get_answer_relevancy_metric(threshold=0.50)

        assert_test(deepeval_case, [hallucination, relevancy])
