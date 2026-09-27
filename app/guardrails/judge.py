"""LLM-as-a-Judge semantic quality and safety evaluation for output guardrails."""

from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from app.config import Settings, get_settings
from app.guardrails.schemas import GuardrailCheckResult, OutputJudgeEvaluation
from app.llm.client import get_structured_model
from app.logging_config import get_logger
from app.prompts.judge import JUDGE_SYSTEM_PROMPT, JUDGE_USER_PROMPT

logger = get_logger(__name__)


# ================= Evaluate the judge evaluation against thresholds =================
def evaluate_judge_thresholds(
    eval_result: OutputJudgeEvaluation,
    settings: Settings | None = None,
) -> tuple[bool, list[str]]:
    """Evaluate whether the structured judge evaluation meets all configured thresholds.

    Returns:
        tuple of (passed: bool, failure_reasons: list[str])
    """
    cfg = settings or get_settings()
    failures: list[str] = []

    if eval_result.relevance < cfg.judge_relevance_threshold:
        failures.append(
            f"Relevance score ({eval_result.relevance:.2f}) is below threshold ({cfg.judge_relevance_threshold:.2f})"
        )
    if eval_result.instruction_adherence < cfg.judge_instruction_threshold:
        failures.append(
            f"Instruction adherence score ({eval_result.instruction_adherence:.2f}) is below threshold ({cfg.judge_instruction_threshold:.2f})"
        )
    if eval_result.clarity < cfg.judge_clarity_threshold:
        failures.append(
            f"Clarity score ({eval_result.clarity:.2f}) is below threshold ({cfg.judge_clarity_threshold:.2f})"
        )
    if eval_result.coherence < cfg.judge_coherence_threshold:
        failures.append(
            f"Coherence score ({eval_result.coherence:.2f}) is below threshold ({cfg.judge_coherence_threshold:.2f})"
        )
    if eval_result.tone < cfg.judge_tone_threshold:
        failures.append(
            f"Tone score ({eval_result.tone:.2f}) is below threshold ({cfg.judge_tone_threshold:.2f})"
        )
    if eval_result.factuality < cfg.judge_factuality_threshold:
        failures.append(
            f"Factuality score ({eval_result.factuality:.2f}) is below threshold ({cfg.judge_factuality_threshold:.2f})"
        )
    if eval_result.overall_quality < cfg.judge_overall_threshold:
        failures.append(
            f"Overall quality score ({eval_result.overall_quality:.2f}) is below threshold ({cfg.judge_overall_threshold:.2f})"
        )

    if not eval_result.passed:
        failures.append("LLM Judge marked evaluation decision as failed.")

    return len(failures) == 0, failures


# ====================== Run the output judge ======================
def evaluate_output_judge(
    tweet: str,
    user_query: str,
    settings: Settings | None = None,
    structured_model: object | None = None,
) -> GuardrailCheckResult:
    """Run LLM-as-a-Judge semantic quality and adherence evaluation on generated tweet output.

    Evaluates:
    - relevance to the requested topic
    - instruction adherence
    - clarity
    - coherence
    - tone
    - factuality/unsupported claims where applicable
    - overall tweet quality

    Returns:
        GuardrailCheckResult with pass/fail status, detailed score metrics, and reasoning.
    """
    cfg = settings or get_settings()

    logger.info("output_llm_judge_evaluating", tweet_len=len(tweet))

    try:
        model: Any = structured_model or get_structured_model(
            schema=OutputJudgeEvaluation,
            model_name=cfg.judge_model,
            temperature=cfg.judge_temperature,
            settings=cfg,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", JUDGE_SYSTEM_PROMPT),
            ("user", JUDGE_USER_PROMPT),
        ])
        messages = prompt.format_messages(
            user_query=user_query,
            tweet=tweet,
        )

        evaluation: OutputJudgeEvaluation = model.invoke(messages)  # type: ignore[assignment]

        passed, failures = evaluate_judge_thresholds(evaluation, settings=cfg)

        if not passed:
            failure_summary = "; ".join(failures)
            reason = f"Output failed semantic quality criteria: {failure_summary}. Notes: {evaluation.reasoning}"
            logger.warning(
                "output_llm_judge_failed",
                relevance=evaluation.relevance,
                instruction_adherence=evaluation.instruction_adherence,
                clarity=evaluation.clarity,
                coherence=evaluation.coherence,
                tone=evaluation.tone,
                factuality=evaluation.factuality,
                overall_quality=evaluation.overall_quality,
                failures=failures,
            )
            return GuardrailCheckResult(
                passed=False,
                reason=reason,
                check_name="output_llm_judge",
                category="quality_violation",
                risk_level="high",
            )

        logger.info(
            "output_llm_judge_passed",
            relevance=evaluation.relevance,
            instruction_adherence=evaluation.instruction_adherence,
            clarity=evaluation.clarity,
            coherence=evaluation.coherence,
            tone=evaluation.tone,
            factuality=evaluation.factuality,
            overall_quality=evaluation.overall_quality,
        )
        return GuardrailCheckResult(
            passed=True,
            reason=evaluation.reasoning,
            check_name="output_llm_judge",
            risk_score=0.0,
        )

    except Exception as exc:
        logger.error("output_llm_judge_error", error=str(exc))
        if not cfg.fail_open_output_judge:
            return GuardrailCheckResult(
                passed=False,
                reason=f"Output LLM Judge service unavailable: {exc}",
                check_name="output_llm_judge_failed_closed",
                category="system_error",
                risk_level="high",
            )

        return GuardrailCheckResult(
            passed=True,
            reason=f"Output LLM Judge skipped due to error: {exc}",
            check_name="output_llm_judge_fallback",
            risk_score=0.0,
        )
