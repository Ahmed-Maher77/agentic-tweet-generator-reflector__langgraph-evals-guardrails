"""Unit tests for app.reflection.reviewer — Reflection Reviewer evaluation node."""

from unittest.mock import MagicMock

from app.config import Settings
from app.reflection.reviewer import apply_threshold_policy, evaluate_tweet
from app.reflection.schemas import ReviewResult


class TestApplyThresholdPolicy:
    """Test deterministic threshold enforcement over raw model outputs."""

    def test_all_scores_above_threshold_passes(self, test_settings: Settings) -> None:
        raw = ReviewResult(
            decision="PASS",
            relevance=0.90,
            clarity=0.85,
            professionalism=0.88,
            engagement=0.75,
            requirement_adherence=0.90,
            issues=[],
            feedback="Looks excellent.",
        )
        result = apply_threshold_policy(raw, settings=test_settings)
        assert result.decision == "PASS"

    def test_single_low_score_forces_revise(self, test_settings: Settings) -> None:
        # Engagement threshold is 0.70; 0.65 should trigger REVISE even if raw says PASS
        raw = ReviewResult(
            decision="PASS",
            relevance=0.95,
            clarity=0.90,
            professionalism=0.90,
            engagement=0.65,
            requirement_adherence=0.95,
            issues=["Hook is too bland."],
            feedback="Improve opening hook.",
        )
        result = apply_threshold_policy(raw, settings=test_settings)
        assert result.decision == "REVISE"

    def test_low_relevance_forces_revise(self, test_settings: Settings) -> None:
        # Relevance threshold is 0.80; 0.75 should trigger REVISE
        raw = ReviewResult(
            decision="REVISE",
            relevance=0.75,
            clarity=0.85,
            professionalism=0.85,
            engagement=0.85,
            requirement_adherence=0.85,
            issues=["Slight topic drift."],
            feedback="Stay on topic.",
        )
        result = apply_threshold_policy(raw, settings=test_settings)
        assert result.decision == "REVISE"


class TestEvaluateTweet:
    """Test evaluate_tweet node execution with mocked model."""

    def test_successful_evaluation(self, test_settings: Settings) -> None:
        mock_model = MagicMock()
        mock_model.invoke.return_value = ReviewResult(
            decision="PASS",
            relevance=0.92,
            clarity=0.88,
            professionalism=0.85,
            engagement=0.80,
            requirement_adherence=0.90,
            issues=[],
            feedback="Strong, clear post.",
        )

        result = evaluate_tweet(
            user_query="Announce our new LangGraph course",
            tweet="Master agentic AI with our new LangGraph course! 🚀 Link below.",
            attempt=1,
            settings=test_settings,
            structured_model=mock_model,
        )

        assert result.decision == "PASS"
        assert result.relevance == 0.92
        mock_model.invoke.assert_called_once()

    def test_evaluation_error_fallback(self, test_settings: Settings) -> None:
        mock_model = MagicMock()
        mock_model.invoke.side_effect = RuntimeError("API timeout")

        result = evaluate_tweet(
            user_query="Announce course",
            tweet="New course out now.",
            attempt=1,
            settings=test_settings,
            structured_model=mock_model,
        )

        # Fallback should return a valid ReviewResult without crashing
        assert isinstance(result, ReviewResult)
        assert result.decision == "PASS"
        assert result.feedback != ""
