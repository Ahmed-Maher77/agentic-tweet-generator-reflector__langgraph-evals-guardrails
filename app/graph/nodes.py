"""LangGraph node implementations connecting guardrails, writer agent, and evaluator."""

from app.agents.writer import run_writer_agent
from app.config import Settings, get_settings
from app.graph.state import AttemptHistoryItem, TweetState
from app.guardrails.input import validate_input
from app.guardrails.output import validate_output
from app.logging_config import get_logger
from app.reflection.reviewer import evaluate_tweet

logger = get_logger(__name__)


# =========== Input Guardrails Node ===========
def input_guardrails_node(
    state: TweetState,
    settings: Settings | None = None,
) -> TweetState:
    """Evaluate incoming user query against deterministic and semantic guardrails."""
    cfg = settings or get_settings()
    user_query = state.get("user_query", "")

    logger.info("node_entered", node="input_guardrails")
    result = validate_input(user_query, settings=cfg)

    new_state = dict(state)
    new_state["attempt_history"] = list(state.get("attempt_history", []))

    if not result.passed:
        logger.warning(
            "input_guardrails_rejected",
            reason=result.reason,
            check_name=result.check_name,
        )
        new_state.update({
            "input_blocked": True,
            "block_reason": result.reason,
            "final_status": "INPUT_BLOCKED",
            "tweet": "",
            "attempt": 0,
        })
    else:
        logger.info("input_guardrails_passed", check_name=result.check_name)
        new_state.update({
            "input_blocked": False,
            "block_reason": None,
            "attempt": 0,
        })

    return new_state  # type: ignore[return-value]


# ================== Tweet Writer Agent Node ====================
def writer_node(
    state: TweetState,
    settings: Settings | None = None,
    llm: object | None = None,
) -> TweetState:
    """Execute the Tweet Writer Agent."""
    cfg = settings or get_settings()
    current_attempt = state.get("attempt", 0) + 1
    max_attempts = state.get("max_attempts", cfg.max_attempts)
    user_query = state.get("user_query", "")

    logger.info(
        "node_entered",
        node="writer",
        attempt=current_attempt,
        max_attempts=max_attempts,
    )

    generated_tweet, search_used = run_writer_agent(
        user_query=user_query,
        attempt=current_attempt,
        max_attempts=max_attempts,
        previous_tweet=state.get("tweet"),
        feedback=state.get("feedback"),
        issues=state.get("issues"),
        search_enabled=state.get("search_enabled", cfg.search_enabled),
        settings=cfg,
        llm=llm,  # type: ignore[arg-type]
    )

    new_state = dict(state)
    new_state.update({
        "attempt": current_attempt,
        "tweet": generated_tweet,
        "search_used": state.get("search_used", False) or search_used,
    })
    return new_state  # type: ignore[return-value]


# ==================== Tweet Reviewer Node ====================
def reflection_node(
    state: TweetState,
    settings: Settings | None = None,
    structured_model: object | None = None,
) -> TweetState:
    """Evaluate generated tweet quality using the Reflection Reviewer evaluation node."""
    cfg = settings or get_settings()
    reflection_enabled = state.get("reflection_enabled", cfg.reflection_enabled)
    user_query = state.get("user_query", "")
    current_tweet = state.get("tweet", "")
    attempt = state.get("attempt", 1)

    logger.info(
        "node_entered",
        node="reflection",
        attempt=attempt,
        reflection_enabled=reflection_enabled,
    )

    new_state = dict(state)
    history: list[AttemptHistoryItem] = list(state.get("attempt_history", []))

    if not reflection_enabled:
        logger.info("reflection_disabled_baseline_mode", attempt=attempt)
        history.append({
            "attempt": attempt,
            "tweet": current_tweet,
            "review": None,
            "passed": True,
        })
        new_state.update({
            "review_passed": True,
            "review": None,
            "feedback": "",
            "issues": [],
            "attempt_history": history,
        })
        return new_state  # type: ignore[return-value]

    # Extract runtime threshold overrides if present
    threshold_overrides = {}
    for key in [
        "relevance_threshold",
        "clarity_threshold",
        "professionalism_threshold",
        "engagement_threshold",
        "requirement_threshold",
    ]:
        val = state.get(key)  # type: ignore[misc]
        if val is not None and isinstance(val, (int, float, str)):
            threshold_overrides[key] = float(val)

    # Run Reflection Evaluator
    review_result = evaluate_tweet(
        user_query=user_query,
        tweet=current_tweet,
        attempt=attempt,
        settings=cfg,
        structured_model=structured_model,
        threshold_overrides=threshold_overrides if threshold_overrides else None,
    )

    is_passed = review_result.decision == "PASS"
    review_dict = review_result.model_dump()

    history.append({
        "attempt": attempt,
        "tweet": current_tweet,
        "review": review_dict,
        "passed": is_passed,
    })

    new_state.update({
        "review_passed": is_passed,
        "review": review_dict,
        "feedback": review_result.feedback,
        "issues": review_result.issues,
        "attempt_history": history,
    })
    return new_state  # type: ignore[return-value]


def output_guardrails_node(
    state: TweetState,
    settings: Settings | None = None,
    structured_model: object | None = None,
) -> TweetState:
    """Final deterministic safety and semantic LLM-as-a-Judge check on the output tweet."""
    cfg = settings or get_settings()
    current_tweet = state.get("tweet", "")
    user_query = state.get("user_query", "")
    attempt = state.get("attempt", 1)
    max_attempts = state.get("max_attempts", cfg.max_attempts)
    review_passed = state.get("review_passed", False)
    current_output_retries = state.get("output_guardrail_retries", 0)

    logger.info(
        "node_entered",
        node="output_guardrails",
        attempt=attempt,
        output_guardrail_retries=current_output_retries,
    )
    result = validate_output(
        tweet=current_tweet,
        user_query=user_query,
        settings=cfg,
        structured_model=structured_model,
    )

    new_state = dict(state)

    if not result.passed:
        next_output_retries = current_output_retries + 1
        max_output_retries = cfg.max_output_guardrail_retries

        if next_output_retries <= max_output_retries:
            logger.warning(
                "output_guardrail_retry_requested",
                reason=result.reason,
                check_name=result.check_name,
                output_guardrail_retries=next_output_retries,
                max_output_retries=max_output_retries,
            )
            new_state.update({
                "output_guardrail_retries": next_output_retries,
                "output_blocked": False,
                "block_reason": result.reason,
                "feedback": (
                    f"Output guardrail violation: {result.reason}. "
                    "Please rewrite the tweet adhering strictly to character limits, safety constraints, and formatting guidelines."
                ),
                "issues": [f"Output guardrail check '{result.check_name}' failed: {result.reason}"],
            })
        else:
            logger.warning(
                "output_guardrail_rejected_max_retries_reached",
                reason=result.reason,
                check_name=result.check_name,
                output_guardrail_retries=next_output_retries,
                max_output_retries=max_output_retries,
            )
            new_state.update({
                "output_guardrail_retries": next_output_retries,
                "output_blocked": True,
                "block_reason": result.reason,
                "final_status": "OUTPUT_BLOCKED",
            })
    else:
        final_status = "SUCCESS" if review_passed or attempt < max_attempts else "MAX_ATTEMPTS_REACHED"
        logger.info("output_guardrails_passed", final_status=final_status)
        new_state.update({
            "output_blocked": False,
            "block_reason": None,
            "final_status": final_status,
        })

    return new_state  # type: ignore[return-value]
