"""Input guardrails: pipeline orchestrator combining deterministic and semantic checks."""

from app.config import Settings
from app.guardrails.deterministic import (
    PROJECT_SPECIFIC_POLICIES,
    SecurityFinding,
    check_deterministic_input,
    evaluate_security_policy,
    run_deterministic_security_detector,
)
from app.guardrails.schemas import GuardrailCheckResult
from app.guardrails.semantic import check_semantic_safety
from app.logging_config import get_logger

logger = get_logger(__name__)


def validate_input(
    user_query: str,
    settings: Settings | None = None,
    structured_model: object | None = None,
) -> GuardrailCheckResult:
    """Complete multi-layered input validation pipeline.

    1. Deterministic checks (instant, zero-cost, offline)
    2. Semantic safety checks (LLM-based)
    """
    # 1. Deterministic checks first
    det_result = check_deterministic_input(user_query, settings=settings)
    if not det_result.passed:
        logger.warning(
            "input_guardrail_deterministic_block",
            reason=det_result.reason,
            check_name=det_result.check_name,
            category=det_result.category,
            risk_level=det_result.risk_level,
        )
        return det_result

    # 2. Semantic safety check
    sem_result = check_semantic_safety(
        user_query,
        settings=settings,
        structured_model=structured_model,
    )
    if not sem_result.passed:
        logger.warning(
            "input_guardrail_semantic_block",
            reason=sem_result.reason,
            check_name=sem_result.check_name,
            category=sem_result.category,
        )
        return sem_result

    return GuardrailCheckResult(
        passed=True,
        reason=None,
        check_name="all_input_guardrails",
    )


__all__ = [
    "PROJECT_SPECIFIC_POLICIES",
    "SecurityFinding",
    "check_deterministic_input",
    "check_semantic_safety",
    "evaluate_security_policy",
    "run_deterministic_security_detector",
    "validate_input",
]
