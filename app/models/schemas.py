"""Common shared domain schemas and data transfer objects."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class ClarificationItem(BaseModel):
    """Specific question to solicit missing context from the user."""

    id: str = Field(description="Unique identifier for the missing detail.")
    question: str = Field(description="Direct question asking for the missing detail.")
    placeholder: str = Field(description="Example answer placeholder.")
    key: str = Field(description="Field name identifier.")
    optional: bool = Field(default=False, description="Whether this detail is optional.")


class TweetGenerationRequest(BaseModel):
    """Input payload for tweet generation requests."""

    query: str = Field(
        ...,
        min_length=1,
        description="The user's topic, announcement, or prompt for the tweet.",
    )
    skip_clarification: bool = Field(
        default=False,
        description="If True, skips the missing details clarification check and generates immediately.",
    )
    clarifications: dict[str, str] | None = Field(
        default=None,
        description="Optional answers provided for previously requested clarifications.",
    )
    max_attempts: int | None = Field(
        default=None,
        ge=1,
        le=10,
        description="Optional override for maximum writer iterations (initial + revisions).",
    )
    reflection_enabled: bool | None = Field(
        default=None,
        description="Optional override to toggle reflection on or off.",
    )
    search_enabled: bool | None = Field(
        default=None,
        description="Optional override to toggle web search grounding on or off.",
    )
    relevance_threshold: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional threshold override for relevance.",
    )
    clarity_threshold: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional threshold override for clarity.",
    )
    professionalism_threshold: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional threshold override for professionalism.",
    )
    engagement_threshold: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional threshold override for engagement.",
    )
    requirement_threshold: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional threshold override for requirement adherence.",
    )


class AttemptRecord(BaseModel):
    """Record of an individual writer attempt and its review result."""

    attempt: int
    tweet: str
    review: dict[str, Any] | None = None
    passed: bool


# ============ Tweet Generation Response Schema ====================
class TweetGenerationResponse(BaseModel):
    status: Literal[
        "SUCCESS",
        "NEEDS_CLARIFICATION",
        "INPUT_BLOCKED",
        "OUTPUT_BLOCKED",
        "MAX_ATTEMPTS_REACHED",
    ]
    tweet: str = ""
    attempts: int = 0
    reflection_enabled: bool = True
    search_used: bool = False
    review: dict[str, Any] | None = None
    attempt_history: list[AttemptRecord] = Field(default_factory=list)
    input_blocked: bool = False
    output_blocked: bool = False
    block_reason: str | None = None
    clarifications_needed: list[ClarificationItem] = Field(default_factory=list)
    clarification_reason: str | None = None
