"""Pydantic schemas for input and output guardrails."""

from pydantic import BaseModel, Field


class GuardrailCheckResult(BaseModel):
    """Result of a guardrail evaluation."""

    passed: bool = Field(description="True if the check passed, False if blocked.")
    reason: str | None = Field(default=None, description="Reason for failure if blocked.")
    check_name: str = Field(description="Name or category of the check executed.")
    category: str | None = Field(default=None, description="Security category of the detected issue.")
    risk_level: str | None = Field(default=None, description="Risk level (e.g. critical, high, medium, low).")
    risk_score: float | None = Field(default=None, description="Aggregate numeric risk score between 0.0 and 1.0.")


class SafetyClassification(BaseModel):
    """Structured output returned by the LLM safety classifier."""

    allowed: bool = Field(
        description="True if the input is a benign tweet generation request, False if malicious/adversarial.",
    )
    reason: str = Field(
        description="Brief justification for the safety classification.",
    )


class OutputJudgeEvaluation(BaseModel):
    """Structured evaluation returned by the LLM-as-a-Judge for semantic output quality."""

    relevance: float = Field(
        description="Score (0.0 to 1.0) evaluating relevance to the requested user topic.",
    )
    instruction_adherence: float = Field(
        description="Score (0.0 to 1.0) evaluating adherence to constraints, style, and instructions.",
    )
    clarity: float = Field(
        description="Score (0.0 to 1.0) evaluating readability, grammar, and clear phrasing.",
    )
    coherence: float = Field(
        description="Score (0.0 to 1.0) evaluating logical flow, consistency, and structural unity.",
    )
    tone: float = Field(
        description="Score (0.0 to 1.0) evaluating appropriateness and engaging professional tone.",
    )
    factuality: float = Field(
        description="Score (0.0 to 1.0) evaluating factual plausibility and absence of unsupported/hallucinated claims.",
    )
    overall_quality: float = Field(
        description="Score (0.0 to 1.0) representing overall holistic tweet quality.",
    )
    reasoning: str = Field(
        description="Detailed justification and evaluation notes for the assigned scores.",
    )
    passed: bool = Field(
        default=True,
        description="True if all quality dimensions meet acceptable standards, False otherwise.",
    )

