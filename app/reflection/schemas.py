"""Pydantic schemas for the Reflection Reviewer evaluation node."""

from typing import Literal

from pydantic import BaseModel, Field


class ReviewResult(BaseModel):
    """Structured evaluation result returned by the Reflection Reviewer LLM evaluator.

    Contains granular scores (0.0 - 1.0) across rubric dimensions,
    a list of concrete weaknesses/issues, actionable feedback, and a PASS/REVISE decision.
    """

    decision: Literal["PASS", "REVISE"] = Field(
        description="Verdict: PASS if quality meets all criteria, REVISE if changes are required.",
    )

    relevance: float = Field(
        ge=0.0,
        le=1.0,
        description="How well the tweet addresses the user's topic and core subject (0.0 to 1.0).",
    )
    clarity: float = Field(
        ge=0.0,
        le=1.0,
        description="Readability, conciseness, and elimination of unnecessary fluff (0.0 to 1.0).",
    )
    professionalism: float = Field(
        ge=0.0,
        le=1.0,
        description="Appropriate tone, credibility, and absence of hyperbolic spam (0.0 to 1.0).",
    )
    engagement: float = Field(
        ge=0.0,
        le=1.0,
        description="Hook strength, natural conversational appeal, and CTA quality (0.0 to 1.0).",
    )
    requirement_adherence: float = Field(
        ge=0.0,
        le=1.0,
        description="Adherence to explicit constraints: length, tone, hashtags, facts (0.0 to 1.0).",
    )

    issues: list[str] = Field(
        default_factory=list,
        description="Specific shortcomings or flaws identified in the draft.",
    )
    feedback: str = Field(
        description="Constructive, actionable guidance for the Tweet Writer Agent to improve the draft.",
    )
