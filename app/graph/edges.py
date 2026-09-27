"""Deterministic conditional routing functions for LangGraph."""

from typing import Literal, cast

from langgraph.graph import END

from app.graph.state import TweetState
from app.logging_config import get_logger

logger = get_logger(__name__)


def route_after_input_guardrails(state: TweetState) -> str:
    """Route after input guardrails check.

    If input is blocked for safety or formatting reasons, bypass generation and end.
    Otherwise, proceed to the Tweet Writer Agent.
    """
    if state.get("input_blocked", False):
        logger.info(
            "routing_input_blocked",
            reason=state.get("block_reason"),
        )
        return cast(str, END)

    return "writer"


def route_after_reflection(state: TweetState) -> Literal["output_guardrails", "writer"]:
    """Deterministic conditional router evaluated after the reflection review node.

    Routing rules:
    1. If review passed (all criteria met) -> proceed to output guardrails.
    2. If maximum attempts reached -> proceed to output guardrails.
    3. If review failed and attempts remain -> loop back to the SAME Tweet Writer Agent.
    """
    attempt = state.get("attempt", 1)
    max_attempts = state.get("max_attempts", 3)
    review_passed = state.get("review_passed", False)

    logger.info(
        "evaluating_routing_decision",
        attempt=attempt,
        max_attempts=max_attempts,
        review_passed=review_passed,
    )

    if review_passed:
        logger.info("route_selected", destination="output_guardrails", reason="review_passed")
        return "output_guardrails"

    if attempt >= max_attempts:
        logger.info(
            "route_selected",
            destination="output_guardrails",
            reason="max_attempts_reached",
        )
        return "output_guardrails"

    logger.info(
        "route_selected",
        destination="writer",
        reason="revision_requested",
        next_attempt=attempt + 1,
    )
    return "writer"


def route_after_output_guardrails(state: TweetState) -> str:
    """Deterministic conditional router evaluated after output guardrails check.

    Routing rules:
    1. If output is blocked (max retries reached or hard failure) -> proceed to END.
    2. If output failed check and retries remain (feedback set for retry) -> loop back to Writer.
    3. If output passed validation -> proceed to END.
    """
    output_blocked = state.get("output_blocked", False)
    block_reason = state.get("block_reason")
    output_retries = state.get("output_guardrail_retries", 0)

    if output_blocked:
        logger.info(
            "routing_output_blocked",
            reason=block_reason,
            output_guardrail_retries=output_retries,
        )
        return cast(str, END)

    # If block_reason is present while output_blocked is False, a retry to the writer was triggered
    if block_reason:
        logger.info(
            "routing_output_guardrail_retry",
            reason=block_reason,
            output_guardrail_retries=output_retries,
        )
        return "writer"

    logger.info("routing_output_guardrails_completed", destination=END)
    return cast(str, END)

