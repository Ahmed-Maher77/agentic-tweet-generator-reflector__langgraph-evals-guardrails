"""State definitions for the LangGraph workflow."""

from typing import Any

from typing_extensions import TypedDict


# =========== Attempt History Item ===========
class AttemptHistoryItem(TypedDict):
    """Structured history record for a single generation-evaluation step."""

    attempt: int
    tweet: str
    review: dict[str, Any] | None
    passed: bool


# =========== Tweet State ===========
class TweetState(TypedDict, total=False):
    """The central state dictionary passed across LangGraph nodes.

    Strictly tracks:
    - User input parameters
    - Iteration counts and attempt bounds
    - Tweet drafts and reviewer feedback
    - Safety and Guardrail evaluations
    - Complete attempt history
    - Final lifecycle status
    """

    # Request & Configuration
    user_query: str
    max_attempts: int
    reflection_enabled: bool
    search_enabled: bool
    relevance_threshold: float
    clarity_threshold: float
    professionalism_threshold: float
    engagement_threshold: float
    requirement_threshold: float

    # Iteration & Writer State
    attempt: int
    tweet: str
    feedback: str
    issues: list[str]
    attempt_history: list[AttemptHistoryItem]
    search_used: bool

    # Guardrails & Review State
    input_blocked: bool
    output_blocked: bool
    block_reason: str | None
    output_guardrail_retries: int
    review_passed: bool
    review: dict[str, Any] | None
    final_status: str
