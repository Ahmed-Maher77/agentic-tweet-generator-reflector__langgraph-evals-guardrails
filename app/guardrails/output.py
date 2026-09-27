"""Output guardrails: deterministic validation and LLM-as-a-Judge semantic evaluation for generated tweets."""

import re

from app.config import Settings, get_settings
from app.guardrails.judge import evaluate_output_judge
from app.guardrails.schemas import GuardrailCheckResult
from app.logging_config import get_logger

logger = get_logger(__name__)

PROMPT_LEAK_PATTERNS = [
    r"you\s+are\s+the\s+tweet\s+writer\s+agent",
    r"you\s+are\s+a\s+specialized\s+security\s+guardrail",
    r"reflection\s+evaluator",
    r"system_prompt",
    r"<user_request>",
    r"<previous_draft>",
    r"<reviewer_feedback>",
]

SECRET_LEAK_PATTERNS = [
    r"sk-[a-zA-Z0-9_-]{20,}",
    r"bearer\s+[a-zA-Z0-9_\-\.]{20,}",
]


# ================= Check Deterministic Output =================
def check_deterministic_output(
    tweet: str,
    settings: Settings | None = None,
) -> GuardrailCheckResult:
    """Run fast deterministic checks on the generated tweet output.

    Enforces:
    1. Output is non-empty and not just whitespace.
    2. Character length <= max_tweet_length (280 chars).
    3. No system prompt leakages or delimiters.
    4. No API keys or secret credential leakages.
    """
    cfg = settings or get_settings()

    if not tweet or not tweet.strip():
        logger.warning("output_guardrail_failed", reason="empty_tweet")
        return GuardrailCheckResult(
            passed=False,
            reason="Generated tweet is empty or whitespace-only.",
            check_name="output_non_empty_check",
            category="validation_error",
            risk_level="critical",
            risk_score=1.0,
        )

    if len(tweet) > cfg.max_tweet_length:
        logger.warning(
            "output_guardrail_failed",
            reason="length_exceeded",
            length=len(tweet),
            limit=cfg.max_tweet_length,
        )
        return GuardrailCheckResult(
            passed=False,
            reason=f"Generated tweet length ({len(tweet)}) exceeds limit ({cfg.max_tweet_length}).",
            check_name="output_length_check",
            category="validation_error",
            risk_level="medium",
            risk_score=0.5,
        )

    # Check for prompt leakage
    for pattern in PROMPT_LEAK_PATTERNS:
        if re.search(pattern, tweet, re.IGNORECASE):
            logger.warning("output_guardrail_failed", reason="prompt_leak_detected")
            return GuardrailCheckResult(
                passed=False,
                reason="Generated tweet contains internal prompt instructions or delimiters.",
                check_name="output_prompt_leak_check",
                category="prompt_leakage",
                risk_level="high",
                risk_score=0.8,
            )

    # Check for secret leakage
    for pattern in SECRET_LEAK_PATTERNS:
        if re.search(pattern, tweet, re.IGNORECASE):
            logger.warning("output_guardrail_failed", reason="secret_leak_detected")
            return GuardrailCheckResult(
                passed=False,
                reason="Generated tweet contains potential secret key leakage.",
                check_name="output_secret_leak_check",
                category="secret_leakage",
                risk_level="critical",
                risk_score=1.0,
            )

    return GuardrailCheckResult(
        passed=True,
        reason=None,
        check_name="output_deterministic_checks_passed",
        risk_score=0.0,
    )


# ================= Validate the output (deterministic + LLM-as-a-judge) =================
def validate_output(
    tweet: str,
    user_query: str | None = None,
    settings: Settings | None = None,
    structured_model: object | None = None,
) -> GuardrailCheckResult:
    """Validate generated tweet output prior to delivery.

    Execution Pipeline:
    1. Deterministic validation (length, emptiness, prompt leaks, credential leaks).
    2. LLM-as-a-Judge semantic evaluation (relevance, instruction adherence, clarity,
       coherence, tone, factuality, overall quality) against configured thresholds.
    """
    cfg = settings or get_settings()

    # 1. Deterministic checks first
    det_result = check_deterministic_output(tweet=tweet, settings=cfg)
    if not det_result.passed:
        return det_result

    # 2. Semantic LLM-as-a-Judge check (if enabled and user_query is provided)
    if cfg.output_judge_enabled and user_query:
        judge_result = evaluate_output_judge(
            tweet=tweet,
            user_query=user_query,
            settings=cfg,
            structured_model=structured_model,
        )
        if not judge_result.passed:
            logger.warning(
                "output_guardrail_judge_blocked",
                reason=judge_result.reason,
                check_name=judge_result.check_name,
            )
            return judge_result

    return GuardrailCheckResult(
        passed=True,
        reason=None,
        check_name="output_guardrails_passed",
        risk_score=0.0,
    )


__all__ = [
    "PROMPT_LEAK_PATTERNS",
    "SECRET_LEAK_PATTERNS",
    "check_deterministic_output",
    "evaluate_output_judge",
    "validate_output",
]
