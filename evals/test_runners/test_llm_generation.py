"""Test runner for LLM generation quality evaluations."""

import pytest
from deepeval import assert_test
from langgraph.graph.state import CompiledStateGraph

from app.graph.state import TweetState
from evals.golden_set import EvalType, GoldenTestCase, load_dataset, to_deepeval_test_case
from evals.metrics import (
    get_answer_relevancy_metric,
    get_engagement_geval,
    get_professionalism_geval,
    get_requirement_adherence_geval,
)


@pytest.mark.llm
class TestLLMGenerationEvaluation:
    """Evaluate core LLM generation quality, tone, engagement, and adherence."""

    @pytest.mark.parametrize(
        "test_case",
        load_dataset(EvalType.LLM),
        ids=lambda tc: tc.id,
    )
    def test_llm_quality_metrics(self, graph: CompiledStateGraph, test_case: GoldenTestCase) -> None:
        """Run DeepEval quality metrics across the LLM generation dataset."""
        state: TweetState = {
            "user_query": test_case.query,
            "max_attempts": 3,
            "reflection_enabled": True,
        }
        result = graph.invoke(state)
        actual_output = result.get("tweet", "")

        assert actual_output != "", f"Empty tweet generated for case {test_case.id}"

        deepeval_case = to_deepeval_test_case(test_case, actual_output)

        relevancy = get_answer_relevancy_metric(threshold=0.50)
        professionalism = get_professionalism_geval(threshold=0.50)
        engagement = get_engagement_geval(threshold=0.50)
        adherence = get_requirement_adherence_geval(threshold=0.50)

        assert_test(deepeval_case, [relevancy, professionalism, engagement, adherence])
