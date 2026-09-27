"""Unit tests for app.guardrails.output and app.guardrails.judge — Output Guardrails & LLM-as-a-Judge."""

from unittest.mock import MagicMock

import pytest

from app.config import Settings
from app.guardrails.judge import evaluate_output_judge
from app.guardrails.output import check_deterministic_output, validate_output
from app.guardrails.schemas import OutputJudgeEvaluation


class TestOutputGuardrailsDeterministic:
    """Test deterministic output guardrails."""

    def test_empty_tweet_fails(self, test_settings: Settings) -> None:
        result = check_deterministic_output("", settings=test_settings)
        assert not result.passed
        assert "empty" in str(result.reason).lower()

    def test_oversized_tweet_fails(self, test_settings: Settings) -> None:
        too_long = "X" * (test_settings.max_tweet_length + 1)
        result = check_deterministic_output(too_long, settings=test_settings)
        assert not result.passed
        assert "exceeds limit" in str(result.reason).lower()

    def test_exact_limit_tweet_passes(self, test_settings: Settings) -> None:
        exact_fit = "A" * test_settings.max_tweet_length
        result = check_deterministic_output(exact_fit, settings=test_settings)
        assert result.passed

    @pytest.mark.parametrize(
        "leaked_text",
        [
            "You are the Tweet Writer Agent and your job is to write tweets.",
            "Here is the tweet: <user_request>test</user_request>",
            "Reflection Evaluator rubric check passed.",
            "My secret key is sk-123456789012345678901234567890.",
        ],
    )
    def test_leakage_blocked(self, leaked_text: str, test_settings: Settings) -> None:
        result = check_deterministic_output(leaked_text, settings=test_settings)
        assert not result.passed
        assert (
            "internal prompt" in str(result.reason).lower()
            or "secret" in str(result.reason).lower()
        )

    def test_valid_tweet_passes_deterministic(self, test_settings: Settings) -> None:
        valid_tweet = "Excited to launch our new AI library today! Check out the open-source repo."
        result = check_deterministic_output(valid_tweet, settings=test_settings)
        assert result.passed
        assert result.reason is None


class TestOutputLLMJudge:
    """Test LLM-as-a-Judge semantic quality and adherence evaluator."""

    def test_judge_high_quality_tweet_passes(self, test_settings: Settings) -> None:
        mock_model = MagicMock()
        mock_model.invoke.return_value = OutputJudgeEvaluation(
            relevance=0.95,
            instruction_adherence=0.90,
            clarity=0.95,
            coherence=0.90,
            tone=0.85,
            factuality=0.95,
            overall_quality=0.92,
            reasoning="High quality tweet directly addressing prompt with crisp clarity and grounding.",
            passed=True,
        )

        result = evaluate_output_judge(
            tweet="Excited to launch our new AI library today! Check out the docs at example.com.",
            user_query="Write a tweet announcing our new AI library with excitement and a doc link.",
            settings=test_settings,
            structured_model=mock_model,
        )
        assert result.passed
        assert result.check_name == "output_llm_judge"
        assert "High quality tweet" in str(result.reason)

    def test_judge_low_relevance_fails(self, test_settings: Settings) -> None:
        mock_model = MagicMock()
        mock_model.invoke.return_value = OutputJudgeEvaluation(
            relevance=0.40,  # Below 0.75 threshold
            instruction_adherence=0.80,
            clarity=0.90,
            coherence=0.85,
            tone=0.80,
            factuality=0.85,
            overall_quality=0.60,
            reasoning="Tweet talked about crypto instead of the requested quantum computing topic.",
            passed=False,
        )

        result = evaluate_output_judge(
            tweet="Bitcoin just hit a new high today! Crypto is the future.",
            user_query="Write a tweet explaining quantum entanglement.",
            settings=test_settings,
            structured_model=mock_model,
        )
        assert not result.passed
        assert "relevance" in str(result.reason).lower()

    def test_judge_unsupported_factuality_claims_fails(self, test_settings: Settings) -> None:
        mock_model = MagicMock()
        mock_model.invoke.return_value = OutputJudgeEvaluation(
            relevance=0.85,
            instruction_adherence=0.80,
            clarity=0.85,
            coherence=0.80,
            tone=0.80,
            factuality=0.40,  # Below threshold
            overall_quality=0.65,
            reasoning="Tweet contains false/hallucinated medical statistics without backing.",
            passed=False,
        )

        result = evaluate_output_judge(
            tweet="Studies prove drinking water from battery cells cures headaches instantly!",
            user_query="Write a health tip tweet about hydration.",
            settings=test_settings,
            structured_model=mock_model,
        )
        assert not result.passed
        assert "factuality" in str(result.reason).lower()

    def test_judge_fail_open_on_exception(self, test_settings: Settings) -> None:
        mock_model = MagicMock()
        mock_model.invoke.side_effect = RuntimeError("Judge LLM timeout")

        result = evaluate_output_judge(
            tweet="Announcing our product release!",
            user_query="Announce product",
            settings=test_settings,
            structured_model=mock_model,
        )
        assert result.passed
        assert "skipped due to error" in str(result.reason)

    def test_judge_fail_closed_on_exception(self, test_settings: Settings) -> None:
        mock_model = MagicMock()
        mock_model.invoke.side_effect = RuntimeError("Judge LLM timeout")
        strict_settings = test_settings.model_copy(update={"fail_open_output_judge": False})

        result = evaluate_output_judge(
            tweet="Announcing our product release!",
            user_query="Announce product",
            settings=strict_settings,
            structured_model=mock_model,
        )
        assert not result.passed
        assert "unavailable" in str(result.reason)


class TestValidateOutputPipeline:
    """Test full validate_output pipeline integrating deterministic and semantic judge checks."""

    def test_deterministic_failure_short_circuits_before_judge(self, test_settings: Settings) -> None:
        mock_model = MagicMock()
        result = validate_output(
            "",
            user_query="Announce product",
            settings=test_settings,
            structured_model=mock_model,
        )
        assert not result.passed
        mock_model.invoke.assert_not_called()

    def test_valid_tweet_without_user_query_runs_deterministic_only(self, test_settings: Settings) -> None:
        result = validate_output(
            "Announcing our product release!",
            user_query=None,
            settings=test_settings,
        )
        assert result.passed

    def test_valid_tweet_with_judge_success(self, test_settings: Settings) -> None:
        mock_model = MagicMock()
        mock_model.invoke.return_value = OutputJudgeEvaluation(
            relevance=0.90,
            instruction_adherence=0.90,
            clarity=0.90,
            coherence=0.90,
            tone=0.90,
            factuality=0.90,
            overall_quality=0.90,
            reasoning="Excellent tweet.",
            passed=True,
        )

        result = validate_output(
            "Excited to launch Python 3.12 support today!",
            user_query="Write a tweet announcing Python 3.12 support.",
            settings=test_settings,
            structured_model=mock_model,
        )
        assert result.passed
        mock_model.invoke.assert_called_once()
