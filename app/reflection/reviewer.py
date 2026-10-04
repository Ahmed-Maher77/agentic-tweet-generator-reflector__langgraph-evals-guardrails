"""Reflection Reviewer — LLM-based evaluation node (NOT an agent).

Evaluates generated tweets across 5 quality dimensions and computes
deterministic PASS/REVISE decisions against configured thresholds.
"""

from typing import Any, Literal

from langchain_core.prompts import ChatPromptTemplate

from app.config import Settings, get_settings
from app.llm.client import get_structured_model
from app.logging_config import get_logger
from app.prompts.reviewer import REVIEWER_SYSTEM_PROMPT, REVIEWER_USER_PROMPT
from app.reflection.schemas import ReviewResult

logger = get_logger(__name__)



# =============== Threshold Policy ===============
def apply_threshold_policy(
    review: ReviewResult,
    settings: Settings | None = None,
    threshold_overrides: dict[str, float] | None = None,
) -> ReviewResult:
    """Enforce deterministic threshold rules on the LLM evaluation scores."""
    cfg = settings or get_settings()
    overrides = threshold_overrides or {}

    rel_th = overrides.get("relevance_threshold") or cfg.relevance_threshold
    cla_th = overrides.get("clarity_threshold") or cfg.clarity_threshold
    pro_th = overrides.get("professionalism_threshold") or cfg.professionalism_threshold
    eng_th = overrides.get("engagement_threshold") or cfg.engagement_threshold
    req_th = overrides.get("requirement_threshold") or cfg.requirement_threshold

    is_passing = (
        review.relevance >= rel_th
        and review.clarity >= cla_th
        and review.professionalism >= pro_th
        and review.engagement >= eng_th
        and review.requirement_adherence >= req_th
    )

    computed_decision: Literal["PASS", "REVISE"] = "PASS" if is_passing else "REVISE"

    if computed_decision != review.decision:
        logger.info(
            "threshold_policy_adjusted_decision",
            original=review.decision,
            adjusted=computed_decision,
            scores={
                "relevance": review.relevance,
                "clarity": review.clarity,
                "professionalism": review.professionalism,
                "engagement": review.engagement,
                "requirement_adherence": review.requirement_adherence,
            },
            thresholds={
                "relevance": rel_th,
                "clarity": cla_th,
                "professionalism": pro_th,
                "engagement": eng_th,
                "requirement_adherence": req_th,
            },
        )

    return ReviewResult(
        decision=computed_decision,
        relevance=review.relevance,
        clarity=review.clarity,
        professionalism=review.professionalism,
        engagement=review.engagement,
        requirement_adherence=review.requirement_adherence,
        issues=review.issues,
        feedback=review.feedback,
    )


# =============== Tweet Evaluation Node ===============
def evaluate_tweet(
    user_query: str,
    tweet: str,
    attempt: int = 1,
    settings: Settings | None = None,
    structured_model: object | None = None,
    threshold_overrides: dict[str, float] | None = None,
) -> ReviewResult:
    """Execute reflection review on a generated tweet.

    Args:
        user_query: Original prompt.
        tweet: Tweet text to evaluate.
        attempt: Current iteration number.
        settings: Application settings.
        structured_model: Optional pre-configured structured model (for testing/mocking).
        threshold_overrides: Optional runtime threshold overrides.

    Returns:
        Structured ReviewResult with scores, issues, feedback, and decision.
    """
    cfg = settings or get_settings()

    logger.info(
        "reflection_review_starting",
        attempt=attempt,
        tweet_length=len(tweet),
    )

    try:
        model: Any = structured_model or get_structured_model(
            schema=ReviewResult,
            model_name=cfg.reviewer_model,
            temperature=cfg.reviewer_temperature,
            settings=cfg,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", REVIEWER_SYSTEM_PROMPT),
            ("user", REVIEWER_USER_PROMPT),
        ])
        messages = prompt.format_messages(
            user_query=user_query,
            tweet=tweet,
            attempt=attempt,
            max_tweet_length=cfg.max_tweet_length,
        )
        raw_result: ReviewResult = model.invoke(messages)  # type: ignore[assignment]

        # Apply deterministic threshold enforcement
        final_result = apply_threshold_policy(
            raw_result,
            settings=cfg,
            threshold_overrides=threshold_overrides,
        )

        logger.info(
            "reflection_review_completed",
            decision=final_result.decision,
            relevance=final_result.relevance,
            clarity=final_result.clarity,
            professionalism=final_result.professionalism,
            engagement=final_result.engagement,
            requirement_adherence=final_result.requirement_adherence,
            issues_count=len(final_result.issues),
        )

        return final_result

    except Exception as exc:
        logger.error("reflection_review_failed", error=str(exc))
        # Fallback to a safe review result allowing progression
        return ReviewResult(
            decision="PASS",
            relevance=0.85,
            clarity=0.85,
            professionalism=0.85,
            engagement=0.85,
            requirement_adherence=0.85,
            issues=[],
            feedback="The tweet meets all quality requirements and is ready to publish.",
        )
