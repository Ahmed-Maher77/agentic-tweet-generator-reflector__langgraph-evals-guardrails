"""Test runner for system-specific tweet constraints, budgets, and hashtag rules."""

import pytest
from langgraph.graph.state import CompiledStateGraph

from app.graph.state import TweetState
from evals.golden_set import EvalType, GoldenTestCase, load_dataset
from evals.metrics import compute_constraint_adherence, compute_lexical_diversity


@pytest.mark.llm
class TestSystemSpecificEvaluation:
    """Evaluate deterministic compliance with tweet formatting, character budgets, and vocabulary rules."""

    @pytest.mark.parametrize(
        "test_case",
        load_dataset(EvalType.SYSTEM_SPECIFIC),
        ids=lambda tc: tc.id,
    )
    def test_system_specific_constraints(
        self, graph: CompiledStateGraph, test_case: GoldenTestCase
    ) -> None:
        """Verify strict character count limits, forbidden words, and required hashtags."""
        state: TweetState = {
            "user_query": test_case.query,
            "max_attempts": 3,
            "reflection_enabled": True,
        }
        result = graph.invoke(state)
        tweet = result.get("tweet", "")

        assert tweet != "", f"Empty tweet returned for {test_case.id}"

        # Evaluate deterministic constraint adherence
        compliance = compute_constraint_adherence(
            prediction=tweet,
            must_include=test_case.must_include,
            forbidden_words=test_case.forbidden_words,
            required_hashtags=test_case.required_hashtags,
            max_char_limit=test_case.max_char_limit,
        )

        assert compliance["length_passed"] is True, f"Length {compliance['char_count']} exceeded limit {test_case.max_char_limit}"
        assert compliance["forbidden_passed"] is True, f"Forbidden word found: {compliance['found_forbidden']}"
        assert compliance["hashtags_passed"] is True, f"Missing required hashtags: {compliance['missing_hashtags']}"

        # Evaluate lexical diversity
        ttr = compute_lexical_diversity(tweet)
        assert ttr > 0.40, f"Lexical diversity (TTR={ttr}) is suspiciously low."
