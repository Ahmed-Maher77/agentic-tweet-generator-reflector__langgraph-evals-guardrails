"""Application configuration loaded from environment variables.

Uses pydantic-settings for typed, validated configuration with env var support.
All configuration is centralized here — no scattered os.getenv() calls.
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file.

    Attributes are grouped by concern: LLM, workflow, thresholds, guardrails, logging.
    Defaults are production-reasonable values that can be overridden via env vars.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- LLM Configuration ---
    openai_api_key: SecretStr = Field(
        ...,
        description="OpenAI API key. Required. Never log or expose this value.",
    )
    writer_model: str = Field(
        default="gpt-4o-mini",
        description="Model used for the Tweet Writer Agent (the only agent).",
    )
    reviewer_model: str = Field(
        default="gpt-4o-mini",
        description="Model used for the Reflection Reviewer (LLM evaluator, NOT an agent).",
    )
    safety_model: str = Field(
        default="gpt-4o-mini",
        description="Model used for the input safety classifier.",
    )
    writer_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for the Tweet Writer Agent. Higher = more creative.",
    )
    reviewer_temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Temperature for the Reflection Reviewer. Lower = more consistent.",
    )

    # --- Workflow Configuration ---
    max_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description=(
            "Maximum total writer invocations per request. "
            "E.g., 3 = 1 initial generation + up to 2 revisions."
        ),
    )
    max_tweet_length: int = Field(
        default=280,
        ge=1,
        le=500,
        description="Maximum tweet length in characters (simple len() counting).",
    )
    reflection_enabled: bool = Field(
        default=True,
        description="Enable reflection loop. False = baseline/single-pass mode.",
    )

    # --- Reflection Thresholds ---
    # All thresholds must be met for a PASS decision.
    relevance_threshold: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
        description="Minimum relevance score for PASS.",
    )
    clarity_threshold: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
        description="Minimum clarity score for PASS.",
    )
    professionalism_threshold: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
        description="Minimum professionalism score for PASS.",
    )
    engagement_threshold: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
        description="Minimum engagement score for PASS.",
    )
    requirement_threshold: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Minimum requirement adherence score for PASS.",
    )

    # --- Input Guardrails ---
    max_input_length: int = Field(
        default=2000,
        ge=1,
        description="Maximum user input length in characters.",
    )

    # --- Logging ---
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL.",
    )


def get_settings() -> Settings:
    """Create and return a validated Settings instance.

    Raises:
        pydantic.ValidationError: If required env vars are missing or invalid.
    """
    return Settings()  # type: ignore[call-arg]
