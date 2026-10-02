"""Application configuration loaded from environment variables.

Uses pydantic-settings for typed, validated configuration with env var support.
All configuration is centralized here — no scattered os.getenv() calls.
"""

from typing import Self

from pydantic import Field, SecretStr, model_validator
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
        extra="ignore",
    )

    # --- LLM Configuration ---
    llm_provider: str = Field(
        default="auto",
        description="LLM provider: 'openai', 'groq', or 'auto' (detects based on available key).",
    )
    openai_api_key: SecretStr | None = Field(
        default=None,
        description="OpenAI API key. Never log or expose this value.",
    )
    groq_api_key: SecretStr | None = Field(
        default=None,
        description="Groq API key. Never log or expose this value.",
    )
    tavily_api_key: SecretStr | None = Field(
        default=None,
        description="Tavily API key for web search grounding (optional, fallback to DuckDuckGo).",
    )
    openai_api_base: str | None = Field(
        default=None,
        description="Custom base URL for OpenAI-compatible endpoint (defaults to https://api.groq.com/openai/v1 for Groq).",
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
    judge_model: str = Field(
        default="gpt-4o-mini",
        description="Model used for the Output LLM-as-a-Judge quality evaluator.",
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
    judge_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Temperature for the Output LLM Judge. Lower = more consistent evaluation.",
    )

    # ================== Validate LLM provider, API keys, and set provider-specific defaults ===================
    @model_validator(mode="after")
    def validate_provider_and_keys(self) -> Self:
        """Validate API keys by checking OpenAI first, then Groq, or raise if neither is available."""
        if self.openai_api_key:
            self.llm_provider = "openai"
        elif self.groq_api_key:
            self.llm_provider = "groq"
            if not self.openai_api_base:
                self.openai_api_base = "https://api.groq.com/openai/v1"
            # Auto-map OpenAI defaults to high-performance Groq models
            if self.writer_model == "gpt-4o-mini":
                self.writer_model = "openai/gpt-oss-20b"
            if self.reviewer_model == "gpt-4o-mini":
                self.reviewer_model = "openai/gpt-oss-20b"
            if self.safety_model == "gpt-4o-mini":
                self.safety_model = "openai/gpt-oss-20b"
            if self.judge_model == "gpt-4o-mini":
                self.judge_model = "openai/gpt-oss-20b"
        else:
            raise ValueError("Neither OPENAI_API_KEY nor GROQ_API_KEY is available. Please provide at least one valid API key.")

        return self

    @property
    def effective_api_key(self) -> SecretStr:
        """Return the active API key based on the configured provider."""
        if self.openai_api_key:
            return self.openai_api_key
        if self.groq_api_key:
            return self.groq_api_key
        raise ValueError("No valid API key configured.")

    @property
    def effective_base_url(self) -> str | None:
        """Return the active base URL for API requests."""
        if self.openai_api_base:
            return self.openai_api_base
        if self.llm_provider == "groq":
            return "https://api.groq.com/openai/v1"
        return None

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
    search_enabled: bool = Field(
        default=True,
        description="Enable real-time web search grounding with Tavily/DuckDuckGo.",
    )
    max_search_results: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of web search result snippets to fetch.",
    )
    max_output_guardrail_retries: int = Field(
        default=1,
        ge=0,
        le=5,
        description="Maximum retry attempts when an output guardrail check fails.",
    )
    max_agent_tool_iterations: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum tool-calling loop iterations for the Tweet Writer Agent.",
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
    deterministic_risk_threshold: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Aggregate risk score threshold at which the deterministic security layer blocks input.",
    )
    fail_open_semantic_safety: bool = Field(
        default=True,
        description="Whether semantic safety check fails open on LLM network/provider errors.",
    )

    # --- Output Guardrails & LLM Judge Configuration ---
    output_judge_enabled: bool = Field(
        default=True,
        description="Enable LLM-as-a-Judge semantic quality evaluation in output guardrails.",
    )
    judge_relevance_threshold: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Minimum relevance score for LLM judge PASS.",
    )
    judge_instruction_threshold: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Minimum instruction adherence score for LLM judge PASS.",
    )
    judge_clarity_threshold: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Minimum clarity score for LLM judge PASS.",
    )
    judge_coherence_threshold: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Minimum coherence score for LLM judge PASS.",
    )
    judge_tone_threshold: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
        description="Minimum tone score for LLM judge PASS.",
    )
    judge_factuality_threshold: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Minimum factuality score for LLM judge PASS.",
    )
    judge_overall_threshold: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Minimum overall quality score for LLM judge PASS.",
    )
    fail_open_output_judge: bool = Field(
        default=True,
        description="Whether output LLM judge fails open on network/provider errors.",
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
