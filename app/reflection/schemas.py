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
        description="How well the tweet addresses the user's topic and core subject (Score from 0.0 to 1.0).",
    )
    clarity: float = Field(
        description="Readability, conciseness, and elimination of unnecessary fluff (Score from 0.0 to 1.0).",
    )
    professionalism: float = Field(
        description="Appropriate tone, credibility, and absence of hyperbolic spam (Score from 0.0 to 1.0).",
    )
    engagement: float = Field(
        description="Hook strength, natural conversational appeal, and CTA quality (Score from 0.0 to 1.0).",
    )
    requirement_adherence: float = Field(
        description="Adherence to explicit constraints: length, tone, hashtags, facts (Score from 0.0 to 1.0).",
    )

    issues: list[str] = Field(
        default_factory=list,
        description="Specific shortcomings or flaws identified in the draft.",
    )
    feedback: str = Field(
        description="Constructive, actionable guidance for the Tweet Writer Agent to improve the draft.",
    )
