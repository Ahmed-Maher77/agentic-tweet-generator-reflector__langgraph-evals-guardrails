"""Common shared domain schemas and data transfer objects."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class TweetGenerationRequest(BaseModel):
    """Input payload for tweet generation requests."""

    query: str = Field(
        ...,
        min_length=1,
        description="The user's topic, announcement, or prompt for the tweet.",
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


class AttemptRecord(BaseModel):
    """Record of an individual writer attempt and its review result."""

    attempt: int
    tweet: str
    review: dict[str, Any] | None = None
    passed: bool


# ============ Tweeet Generation Response Schema ====================
class TweetGenerationResponse(BaseModel):
    status: Literal["SUCCESS", "INPUT_BLOCKED", "OUTPUT_BLOCKED", "MAX_ATTEMPTS_REACHED"]
    tweet: str = ""
    attempts: int = 0
    reflection_enabled: bool = True
    search_used: bool = False
    review: dict[str, Any] | None = None
    attempt_history: list[AttemptRecord] = Field(default_factory=list)
    input_blocked: bool = False
    output_blocked: bool = False
    block_reason: str | None = None
