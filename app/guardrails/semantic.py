"""Semantic LLM-based safety and prompt-injection classification guardrail."""

from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from app.config import Settings, get_settings
from app.guardrails.schemas import GuardrailCheckResult, SafetyClassification
from app.llm.client import get_structured_model
from app.logging_config import get_logger
from app.prompts.safety import SAFETY_SYSTEM_PROMPT, SAFETY_USER_PROMPT

logger = get_logger(__name__)


# ==================== Semantic Safety Check ====================
def check_semantic_safety(
    user_query: str,
    settings: Settings | None = None,
    structured_model: object | None = None,
) -> GuardrailCheckResult:
    """Perform LLM-based safety and prompt-injection check."""
    cfg = settings or get_settings()

    try:
        model: Any = structured_model or get_structured_model(
            schema=SafetyClassification,
            model_name=cfg.safety_model,
            temperature=0.0,
            settings=cfg,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", SAFETY_SYSTEM_PROMPT),
            ("user", SAFETY_USER_PROMPT),
        ])
        messages = prompt.format_messages(user_query=user_query)
        result: SafetyClassification = model.invoke(messages)  # type: ignore[assignment]

        if not result.allowed:
            return GuardrailCheckResult(
                passed=False,
                reason=result.reason or "Query failed safety policy.",
                check_name="semantic_safety_check",
                category="semantic_safety_violation",
                risk_level="high",
                risk_score=1.0,
            )

        return GuardrailCheckResult(
            passed=True,
            reason=result.reason,
            check_name="semantic_safety_check",
            risk_score=0.0,
        )
    except Exception as exc:
        logger.error("semantic_safety_check_error", error=str(exc))
        if not cfg.fail_open_semantic_safety:
            return GuardrailCheckResult(
                passed=False,
                reason=f"Semantic safety service unavailable: {exc}",
                check_name="semantic_safety_check_failed_closed",
                category="system_error",
                risk_level="high",
            )

        return GuardrailCheckResult(
            passed=True,
            reason=f"Semantic check skipped due to error: {exc}",
            check_name="semantic_safety_check_fallback",
            risk_score=0.0,
        )
